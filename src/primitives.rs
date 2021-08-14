use pyo3::prelude::*;
use pyo3::types::{PyDict, PyString, PyTuple};
use unicode_segmentation::{Graphemes, UnicodeSegmentation};

use crate::result;
use crate::trampoline;

#[pyclass]
pub struct LiteralParser {
    expected_string: String,
}

#[pymethods]
impl LiteralParser {
    #[new]
    fn new(expected: String) -> Self {
        LiteralParser {
            expected_string: expected,
        }
    }
    #[call]
    fn __call__(
        &self,
        py: Python,
        stream: PyObject,
        continuation: PyObject,
    ) -> PyResult<trampoline::Call> {
        let result = self.parse(py, &stream, &continuation)?;
        Ok(trampoline::Call {
            function: Some(continuation),
            args: Some(PyTuple::new(py, &[stream, result.into_py(py)]).into_py(py)),
            kwargs: Some(PyDict::new(py).into_py(py)),
        })
    }
}

impl LiteralParser {
    pub fn graphemes<'a>(&'a self) -> Graphemes<'a> {
        self.expected_string.graphemes(true)
    }

    fn parse(
        &self,
        py: Python,
        stream: &PyObject,
        continuation: &PyObject,
    ) -> PyResult<result::Result> {
        for expected_character in self.graphemes() {
            let next_character = stream
                .call_method(py, "next", (), None)?
                .into_ref(py)
                .str()?
                .to_str()?;
            if expected_character == next_character {
                stream.call_method(py, "read", (), None)?;
            } else {
                let position = stream.call_method(py, "position", (), None)?;
                return Ok(result::failure(
                    py,
                    format!(
                        "Expected `{}` but found `{}`.",
                        &self.expected_string, next_character
                    ),
                    position.extract(py)?,
                ));
            }
        }
        Ok(result::success(
            py,
            PyObject::from(PyString::new(py, &self.expected_string)),
        ))
    }
}

pub fn initialize_module(module: &PyModule) -> PyResult<()> {
    module.add_class::<LiteralParser>()?;
    Ok(())
}

#[cfg(test)]
mod tests {}
