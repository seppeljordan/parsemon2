use pyo3::prelude::*;

#[pyclass]
struct Stream {
    py_stream: PyObject,
}

pub fn initialize_module(module: &PyModule) -> PyResult<()> {
    module.add_class::<Stream>()?;
    Ok(())
}
