use gguf_metadata_modifier::{GGUFFile, GGUFMetadata};
use serde_json::Value;
use std::fs;
use tempfile::NamedTempFile;

fn create_test_gguf_file() -> NamedTempFile {
    let file = NamedTempFile::new().unwrap();
    let path = file.path().to_str().unwrap();

    let mut gguf = GGUFFile {
        path: path.to_string(),
        metadata: vec![
            GGUFMetadata {
                key: "test_string".to_string(),
                value: Value::String("test_value".to_string()),
                value_type: "4".to_string(),
            },
            GGUFMetadata {
                key: "test_int".to_string(),
                value: Value::Number(42.into()),
                value_type: "2".to_string(),
            },
            GGUFMetadata {
                key: "test_float".to_string(),
                value: Value::Number(serde_json::Number::from_f64(3.14).unwrap()),
                value_type: "3".to_string(),
            },
            GGUFMetadata {
                key: "test_bool".to_string(),
                value: Value::Bool(true),
                value_type: "1".to_string(),
            },
        ],
    };
    gguf.save().unwrap();
    file
}

#[test]
fn test_new_gguf_file() {
    let file = create_test_gguf_file();
    let path = file.path().to_str().unwrap();

    let gguf = GGUFFile::new(path).unwrap();
    assert_eq!(gguf.metadata.len(), 4);
    assert_eq!(gguf.metadata[0].key, "test_string");
    assert_eq!(gguf.metadata[0].value, Value::String("test_value".to_string()));
    assert_eq!(gguf.metadata[1].key, "test_int");
    assert_eq!(gguf.metadata[1].value, Value::Number(42.into()));
    assert_eq!(gguf.metadata[2].key, "test_float");
    assert_eq!(gguf.metadata[2].value, Value::Number(serde_json::Number::from_f64(3.14).unwrap()));
    assert_eq!(gguf.metadata[3].key, "test_bool");
    assert_eq!(gguf.metadata[3].value, Value::Bool(true));
}

#[test]
fn test_modify_metadata() {
    let file = create_test_gguf_file();
    let path = file.path().to_str().unwrap();

    let mut gguf = GGUFFile::new(path).unwrap();
    gguf.modify_metadata("test_string", Value::String("new_value".to_string()), "4").unwrap();
    gguf.modify_metadata("new_key", Value::Number(100.into()), "2").unwrap();

    let gguf = GGUFFile::new(path).unwrap();
    assert_eq!(gguf.metadata.len(), 5);
    assert_eq!(gguf.metadata[0].value, Value::String("new_value".to_string()));
    assert_eq!(gguf.metadata[4].key, "new_key");
    assert_eq!(gguf.metadata[4].value, Value::Number(100.into()));
}

#[test]
fn test_remove_metadata() {
    let file = create_test_gguf_file();
    let path = file.path().to_str().unwrap();

    let mut gguf = GGUFFile::new(path).unwrap();
    gguf.remove_metadata("test_int").unwrap();

    let gguf = GGUFFile::new(path).unwrap();
    assert_eq!(gguf.metadata.len(), 3);
    assert!(!gguf.metadata.iter().any(|m| m.key == "test_int"));
}

#[test]
fn test_export_import_metadata() {
    let file = create_test_gguf_file();
    let path = file.path().to_str().unwrap();

    let export_file = NamedTempFile::new().unwrap();
    let export_path = export_file.path().to_str().unwrap();

    // Export metadata
    let gguf = GGUFFile::new(path).unwrap();
    gguf.export_metadata(export_path).unwrap();

    // Modify the original file
    let mut gguf = GGUFFile::new(path).unwrap();
    gguf.remove_metadata("test_int").unwrap();
    gguf.remove_metadata("test_float").unwrap();

    // Import metadata back
    gguf.import_metadata(export_path).unwrap();

    // Check if the metadata was restored
    let gguf = GGUFFile::new(path).unwrap();
    assert_eq!(gguf.metadata.len(), 4);
    assert!(gguf.metadata.iter().any(|m| m.key == "test_int"));
    assert!(gguf.metadata.iter().any(|m| m.key == "test_float"));
}

#[test]
fn test_search_metadata() {
    let file = create_test_gguf_file();
    let path = file.path().to_str().unwrap();

    let gguf = GGUFFile::new(path).unwrap();
    let results = gguf.search_metadata("test");
    assert_eq!(results.len(), 4);

    let results = gguf.search_metadata("int");
    assert_eq!(results.len(), 1);
    assert_eq!(results[0].key, "test_int");

    let results = gguf.search_metadata("nonexistent");
    assert_eq!(results.len(), 0);
}

#[test]
fn test_invalid_gguf_file() {
    let file = NamedTempFile::new().unwrap();
    let path = file.path().to_str().unwrap();

    // Write some random data to the file
    fs::write(path, b"This is not a GGUF file").unwrap();

    let result = GGUFFile::new(path);
    assert!(result.is_err());
}

#[test]
fn test_modify_nonexistent_file() {
    let result = GGUFFile::new("nonexistent_file.gguf");
    assert!(result.is_err());
}

#[test]
fn test_large_metadata() {
    let file = NamedTempFile::new().unwrap();
    let path = file.path().to_str().unwrap();

    let mut gguf = GGUFFile {
        path: path.to_string(),
        metadata: vec![],
    };

    // Add 1000 metadata entries
    for i in 0..1000 {
        gguf.metadata.push(GGUFMetadata {
            key: format!("key_{}", i),
            value: Value::String(format!("value_{}", i)),
            value_type: "4".to_string(),
        });
    }

    gguf.save().unwrap();

    // Read the file back and check if all metadata is present
    let gguf = GGUFFile::new(path).unwrap();
    assert_eq!(gguf.metadata.len(), 1000);
    for i in 0..1000 {
        assert_eq!(gguf.metadata[i].key, format!("key_{}", i));
        assert_eq!(gguf.metadata[i].value, Value::String(format!("value_{}", i)));
    }
}
