use pyo3::class::number::PyNumberProtocol;
use pyo3::gc::{PyGCProtocol, PyVisit};
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::PyTraverseError;

mod primitives;
mod result;
mod trampoline;

fn add_submodule<F>(
    py: Python<'_>,
    name: &str,
    initialize_submodule: F,
    module: &PyModule,
) -> PyResult<()>
where
    F: Fn(&PyModule) -> PyResult<()>,
{
    let submodule = PyModule::new(py, name)?;
    initialize_submodule(submodule)?;
    module.add_submodule(submodule)?;
    Ok(())
}

#[pymodule]
fn extensions(py: Python<'_>, module: &PyModule) -> PyResult<()> {
    add_submodule(py, "result", result::initialize_module, &module)?;
    add_submodule(py, "trampoline", trampoline::initialize_trampoline, &module)?;
    add_submodule(py, "primitives", primitives::initialize_module, &module)?;
    Ok(())
}
