use pyo3::prelude::*;
mod jenkins;
mod models;
/// A Python module implemented in Rust.
#[pymodule]
mod logmill {

    use super::models::{BuildOutcome, ParsedLog, TestSummary};
    use pyo3::prelude::*;

    /// Formats the sum of two numbers as string.
    #[pyfunction]
    fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
        Ok((a + b).to_string())
    }

    /// Make sample jenkins parser return.
    #[pyfunction]
    fn sample_jenkins_return() -> PyResult<ParsedLog> {
        let errors = vec![
            "[Build] error[E0499]: cannot borrow `x` as mutable more than once".to_string(),
            "[Build] Build step 'Execute shell' marked build as failure".to_string(),
            "[Build] Script exited with code 1".to_string(),
        ];
        let warnings = vec!["[Build] [WARNING] 3 deprecation warnings emitted".to_string()];
        let duration_seconds = Some(17.0);
        let severity_score = 83 as u8;
        let outcome = Some(BuildOutcome::Failure);
        let test_summary = Some(TestSummary {
            passed: 7,
            failed: 3,
            skipped: 0,
        });

        let parser_return = ParsedLog {
            errors,
            warnings,
            duration_seconds,
            severity_score,
            outcome,
            test_summary,
        };

        Ok(parser_return)
    }
}
