use pyo3::class::number::PyNumberProtocol;
use pyo3::gc::{PyGCProtocol, PyVisit};
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::PyTraverseError;

mod trampoline;

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

#[pyproto]
impl PyGCProtocol for Result {
    fn __traverse__(&self, visit: PyVisit) -> std::result::Result<(), PyTraverseError> {
        if let Some(value) = &self.value {
            visit.call(value)?;
        }
        Ok(())
    }
    fn __clear__(&mut self) {
        self.value = None;
    }
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
}

#[pyproto]
impl<'e> PyNumberProtocol<'e> for Result {
    fn __add__(lhs: Result, rhs: Result) -> Result {
        if lhs.is_failure() {
            if rhs.is_failure() {
                let mut failures = Vec::new();
                failures.append(&mut lhs.failures.iter().cloned().collect());
                failures.append(&mut rhs.failures.iter().cloned().collect());
                Result {
                    value: None,
                    failures,
                }
            } else {
                rhs
            }
        } else {
            lhs
        }
    }
}

#[pyfunction]
fn success<'p>(_python: Python<'p>, value: PyObject) -> Result {
    Result {
        value: Some(value),
        failures: vec![],
    }
}

#[pyfunction]
fn failure<'p>(_python: Python<'p>, message: String, position: usize) -> Result {
    Result {
        value: None,
        failures: vec![Failure { message, position }],
    }
}

fn initialize_result(module: &PyModule) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(success, module)?)?;
    module.add_function(wrap_pyfunction!(failure, module)?)?;
    module.add_class::<Failure>()?;
    module.add_class::<Result>()?;
    Ok(())
}

#[pymodule]
fn extensions(py: Python<'_>, module: &PyModule) -> PyResult<()> {
    let result_submodule = PyModule::new(py, "result")?;
    initialize_result(result_submodule)?;
    module.add_submodule(result_submodule)?;
    let trampoline_submodule = PyModule::new(py, "trampoline")?;
    trampoline::initialize_trampoline(trampoline_submodule)?;
    module.add_submodule(trampoline_submodule)?;
    Ok(())
}
