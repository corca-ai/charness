fn main() {
    let exit_code = match std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
        repograph::run(std::env::args().skip(1))
    })) {
        Ok(exit_code) => exit_code,
        Err(payload) => {
            eprintln!(
                "internal error: repograph panicked: {}",
                panic_message(&payload)
            );
            70
        }
    };
    std::process::exit(exit_code);
}

fn panic_message(payload: &Box<dyn std::any::Any + Send>) -> String {
    if let Some(message) = payload.downcast_ref::<&str>() {
        return (*message).to_string();
    }
    if let Some(message) = payload.downcast_ref::<String>() {
        return message.clone();
    }
    "non-string panic payload".to_string()
}
