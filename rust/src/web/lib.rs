use wasm_bindgen::prelude::*;

use nmstate::{NetworkState, NetworkPolicy};
use serde_yaml::from_str;

// Expose a function to JavaScript
#[wasm_bindgen]
pub fn expand_policy(state: &str, policy: &str) -> String {
    let network_state = match from_str::<NetworkState>(state) {
        Ok(state) => state,
        Err(e) => return e.to_string(),
    };

    let network_policy = match from_str::<NetworkPolicy>(policy) {
        Ok(policy) => policy,
        Err(e) => return e.to_string(),
    };

    let captured_states = match network_policy.capture.execute(&network_state) {
        Ok(captured_states) => captured_states,
        Err(e) => return e.to_string(),
    };

    let expanded_state = match network_policy.desired.fill_with_captured_data(&captured_states) {
        Ok(expanded_state) => expanded_state,
        Err(e) => return e.to_string(),
    };

    if expanded_state.is_empty() {
        return "".to_string();
    };

    let serialized = match serde_yaml::to_string(&expanded_state) {
        Ok(serialized) => serialized,
        Err(e) => return e.to_string(),
    };

    return serialized;
}
