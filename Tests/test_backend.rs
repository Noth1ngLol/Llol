#[test]
fn test_end_to_end_workflow() {
    let file = create_sample_file();
    let path = file.path().to_str().unwrap();

    let mut gguf = GGUFFile::new(path).unwrap();

    // Modify metadata
    gguf.modify_metadata("model_name", Value::String("New Model Name".to_string()), "string").unwrap();

    // Add a new field
    gguf.modify_metadata("learning_rate", Value::Number(0.01.into()), "float").unwrap();

    // Save and reload the file
    gguf.save().unwrap();
    let reloaded_gguf = GGUFFile::new(path).unwrap();

    // Verify changes persisted
    let updated_model = reloaded_gguf.metadata.iter().find(|m| m.key == "model_name").unwrap();
    assert_eq!(updated_model.value, Value::String("New Model Name".to_string()));

    let new_field = reloaded_gguf.metadata.iter().find(|m| m.key == "learning_rate").unwrap();
    assert_eq!(new_field.value, Value::Number(0.01.into()));
}
