use regex::Regex;
use std::sync::OnceLock;

static RE_TIMESTAMP: OnceLock<Regex> = OnceLock::new();

fn re_timestamp() -> &'static Regex {
    RE_TIMESTAMP.get_or_init(|| {
        // Matches: 10:23:41  or  2024-01-15 10:23:41  or  10:23:41.123
        Regex::new(r"(\d{2}:\d{2}:\d{2})(?:\.\d+)?").unwrap()
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_re_timestamp() {
        let text = include_str!("log_samples/jenkins.log");

        let re = re_timestamp();

        let dates: Vec<&str> = re.find_iter(text).map(|m| m.as_str()).collect();
        println!("{:?}", dates);
        // for line in raw_log_file.lines()    {
        //     let trimmed = line.trim();
        //     if trimmed.is_empty() {
        //         continue;
        //     }
        //     if let Some(cap) = re.find(raw_log_file) {
        //     for c in cap.iter() {
        //         println!("{:?}", c);
        //     }
        // }
        // }
    }
}
