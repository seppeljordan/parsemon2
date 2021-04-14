use pyo3::exceptions::PyException;
use pyo3::gc::{PyGCProtocol, PyVisit};
use pyo3::prelude::*;
use pyo3::type_object::PyTypeInfo;
use pyo3::types::{PyDict, PyTuple};
use pyo3::wrap_pyfunction;
use pyo3::PyTraverseError;

#[pyclass]
#[derive(Clone)]
pub struct Call {
    function: Option<PyObject>,
    args: Option<PyObject>,
    kwargs: Option<PyObject>,
}

#[pymethods]
impl Call {
    #[new]
    #[args(args = "*", kwargs = "**")]
    fn new(
        py: Python,
        function: PyObject,
        args: &PyTuple,
        kwargs: Option<&PyDict>,
    ) -> PyResult<Self> {
        Ok(Self {
            function: Some(function),
            args: Some(args.to_object(py)),
            kwargs: match kwargs {
                Some(dict) => Some(dict.to_object(py)),
                None => Some(PyDict::new(py).to_object(py)),
            },
        })
    }
}

#[pyproto]
impl PyGCProtocol for Call {
    fn __traverse__(&self, visit: PyVisit) -> std::result::Result<(), PyTraverseError> {
        if let Some(function) = &self.function {
            visit.call(function)?;
        }
        if let Some(args) = &self.args {
            visit.call(args)?;
        }
        if let Some(kwargs) = &self.kwargs {
            visit.call(kwargs)?;
        }
        Ok(())
    }

    fn __clear__(&mut self) {
        self.function = None;
        self.args = None;
        self.kwargs = None;
    }
}

impl Call {
    fn get_args<'py>(&'py self, py: Python<'py>) -> PyResult<&'py PyTuple> {
        match &self.args {
            Some(args) => args.extract(py),
            None => Err(PyException::new_err(
                "Could not get arguments for trampoline call",
            )),
        }
    }
    fn get_kwargs<'py>(&'py self, py: Python<'py>) -> PyResult<&'py PyDict> {
        match &self.kwargs {
            Some(kwargs) => kwargs.extract(py),
            None => Err(PyException::new_err(
                "Could not get keyword arguments for trampoline call",
            )),
        }
    }
    fn get_function(&self) -> PyResult<&PyObject> {
        match &self.function {
            Some(function) => Ok(function),
            None => Err(PyException::new_err(
                "Could not get function for trampoline call",
            )),
        }
    }
}

#[pyclass]
#[derive(Clone)]
pub struct Result {
    value: Option<PyObject>,
}

#[pymethods]
impl Result {
    #[new]
    fn new(value: PyObject) -> PyResult<Self> {
        Ok(Self { value: Some(value) })
    }
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
        self.value = None
    }
}

#[pyfunction(args = "*", kwargs = "**")]
fn with_trampoline(
    py: Python,
    trampoline: &PyAny,
    args: &PyTuple,
    kwargs: Option<&PyDict>,
) -> PyResult<PyObject> {
    let mut object = trampoline.call(args, kwargs)?;
    while Call::is_type_of(object) {
        let call_object = object.extract::<Call>()?;
        let function = call_object.get_function()?;
        let args = call_object.get_args(py)?;
        let kwargs = call_object.get_kwargs(py)?;
        object = function.call(py, args, Some(kwargs))?.into_ref(py);
    }
    Ok(object.extract::<Result>()?.value.unwrap())
}

pub fn initialize_trampoline(module: &PyModule) -> PyResult<()> {
    module.add_class::<Result>()?;
    module.add_class::<Call>()?;
    module.add_function(wrap_pyfunction!(with_trampoline, module)?)?;
    Ok(())
}
