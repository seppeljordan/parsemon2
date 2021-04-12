use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::type_object::PyTypeInfo;
use pyo3::types::{PyDict, PyTuple};


#[pyclass]
#[derive(Clone)]
pub struct Call {
    function: PyObject,
    args: PyObject,
    kwargs: PyObject,
}

#[pymethods]
impl Call {
    #[new]
    #[args(args="*", kwargs="**")]
    fn new(py: Python, function: PyObject, args: &PyTuple, kwargs: Option<&PyDict>) -> PyResult<Self>{
	Ok(Self {
	    function:function,
	    args: args.to_object(py),
	    kwargs: match kwargs {
		Some(dict) => dict.to_object(py),
		None => PyDict::new(py).to_object(py),
	    }
	})
    }
}


#[pyclass]
#[derive(Clone)]
pub struct Result {
    value: PyObject
}

#[pymethods]
impl Result {
    #[new]
    fn new(value: PyObject) -> PyResult<Self> {
	Ok(Self {
	    value: value
	})
    }
}

#[pyfunction(args="*", kwargs="**")]
fn with_trampoline(py: Python, trampoline: &PyAny, args: &PyTuple, kwargs: Option<&PyDict>) -> PyResult<PyObject> {
    let mut object = trampoline.call(args, kwargs)?;
    while Call::is_type_of(object) {	
	let call_object = object.extract::<Call>()?.clone();
	let function = call_object.function;
	let args = call_object.args.extract::<&PyTuple>(py)?;
	let kwargs = call_object.kwargs.extract::<&PyDict>(py)?;
	object = function.call(py, args, Some(kwargs))?.into_ref(py);
    }
    Ok(object.extract::<Result>()?.value)
}


pub fn initialize_trampoline(module: &PyModule) -> PyResult<()> {
    module.add_class::<Result>()?;
    module.add_class::<Call>()?;
    module.add_function(wrap_pyfunction!(with_trampoline, module)?)?;
    Ok(())
}
