use pyo3::gc::PyVisit;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::PyTraverseError;

#[pyclass]
#[derive(Clone)]
pub struct Failure {
    #[pyo3(get)]
    message: String,
    #[pyo3(get)]
    position: usize,
}

#[pyclass]
#[derive(Clone)]
pub struct Result {
    value: Option<PyObject>,
    failures: Vec<Failure>,
}

#[pymethods]
impl Result {
    pub fn is_failure(&self) -> bool {
        self.failures.len() > 0
    }

    pub fn map_value(&self, py: Python, mapping: PyObject) -> PyResult<Self> {
        match &self.value {
            Some(old_value) => {
                let mut other = self.clone();
                other.value = mapping.call1(py, (old_value,)).ok();
                Ok(other)
            }
            None => Ok(self.clone()),
        }
    }

    #[getter]
    pub fn value(&self, py: Python) -> PyResult<PyObject> {
        match &self.value {
            Some(value) => Ok(value.clone()),
            None => Ok(py.None()),
        }
    }

    pub fn get_failures(&self, _py: Python) -> PyResult<Vec<Failure>> {
        Ok(self.failures.iter().cloned().collect())
    }

    fn __traverse__(&self, visit: PyVisit) -> std::result::Result<(), PyTraverseError> {
        if let Some(value) = &self.value {
            visit.call(value)?;
        }
        Ok(())
    }
    fn __clear__(&mut self) {
        self.value = None;
    }

    fn __add__(&self, rhs: Result) -> PyResult<Result> {
        if self.is_failure() {
            if rhs.is_failure() {
                let mut failures = Vec::new();
                failures.append(&mut self.failures.iter().cloned().collect());
                failures.append(&mut rhs.failures.iter().cloned().collect());
                Ok(Result {
                    value: None,
                    failures,
                })
            } else {
                Ok(rhs)
            }
        } else {
            Ok(self.clone())
        }
    }
}

#[pyfunction]
pub fn success<'p>(_python: Python<'p>, value: PyObject) -> Result {
    Result {
        value: Some(value),
        failures: vec![],
    }
}

#[pyfunction]
pub fn failure<'p>(_python: Python<'p>, message: String, position: usize) -> Result {
    Result {
        value: None,
        failures: vec![Failure { message, position }],
    }
}

pub fn initialize_module(module: &PyModule) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(success, module)?)?;
    module.add_function(wrap_pyfunction!(failure, module)?)?;
    module.add_class::<Failure>()?;
    module.add_class::<Result>()?;
    Ok(())
}
