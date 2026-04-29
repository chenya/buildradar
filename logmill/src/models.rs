use pyo3::prelude::*;

#[pyclass]
#[derive(Debug, Clone)]
pub enum BuildOutcome {
    Success,
    Failure,
    Unstable,
    Aborted,
}

#[pyclass]
#[derive(Debug, Clone)]
pub struct TestSummary {
    #[pyo3(get)]
    pub passed: u32,
    #[pyo3(get)]
    pub failed: u32,
    #[pyo3(get)]
    pub skipped: u32,
}

#[pyclass]
#[derive(Debug)]
pub struct ParsedLog {
    #[pyo3(get)]
    pub errors: Vec<String>,
    #[pyo3(get)]
    pub warnings: Vec<String>,
    #[pyo3(get)]
    pub duration_seconds: Option<f64>,
    #[pyo3(get)]
    pub severity_score: u8,
    #[pyo3(get)]
    pub test_summary: Option<TestSummary>,
    #[pyo3(get)]
    pub outcome: Option<BuildOutcome>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_name() {}
}
