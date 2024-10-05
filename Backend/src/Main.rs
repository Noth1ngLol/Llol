use std::env;
use std::process;
use gguf_metadata_modifier::{GGUFFile, GGUFMetadata};
use serde_json::Value;

fn print_usage() {
    println!("Usage:");
    println!("  gguf_metadata_modifier <command> [args]");
    println!("");
    println!("Commands:");
    println!("  modify <file> <key> <value> <type>  Modify or add metadata");
    println!("  remove <file> <key>                 Remove metadata");
    println!("  export <file> <export_path>         Export metadata to JSON");
    println!("  import <file> <import_path>         Import metadata from JSON");
    println!("  search <file> <search_key>          Search metadata by key");
}

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        print_usage();
        process::exit(1);
    }

    let command = &args[1];

    match command.as_str() {
        "modify" => {
            if args.len() != 6 {
                println!("Invalid number of arguments for modify command");
                print_usage();
                process::exit(1);
            }
            let file_path = &args[2];
            let key = &args[3];
            let value = &args[4];
            let value_type = &args[5];

            let mut gguf = match GGUFFile::new(file_path) {
                Ok(file) => file,
                Err(e) => {
                    println!("Error opening GGUF file: {}", e);
                    process::exit(1);
                }
            };

            let value = match value_type {
                "string" => Value::String(value.to_string()),
                "int" => Value::Number(value.parse().unwrap()),
                "float" => Value::Number(serde_json::Number::from_f64(value.parse().unwrap()).unwrap()),
                "bool" => Value::Bool(value.parse().unwrap()),
                _ => {
                    println!("Invalid value type. Supported types are: string, int, float, bool");
                    process::exit(1);
                }
            };

            if let Err(e) = gguf.modify_metadata(key, value, value_type) {
                println!("Error modifying metadata: {}", e);
                process::exit(1);
            }

            println!("Metadata modified successfully");
        }
        "remove" => {
            if args.len() != 4 {
                println!("Invalid number of arguments for remove command");
                print_usage();
                process::exit(1);
            }
            let file_path = &args[2];
            let key = &args[3];

            let mut gguf = match GGUFFile::new(file_path) {
                Ok(file) => file,
                Err(e) => {
                    println!("Error opening GGUF file: {}", e);
                    process::exit(1);
                }
            };

            if let Err(e) = gguf.remove_metadata(key) {
                println!("Error removing metadata: {}", e);
                process::exit(1);
            }

            println!("Metadata removed successfully");
        }
        "export" => {
            if args.len() != 4 {
                println!("Invalid number of arguments for export command");
                print_usage();
                process::exit(1);
            }
            let file_path = &args[2];
            let export_path = &args[3];

            let gguf = match GGUFFile::new(file_path) {
                Ok(file) => file,
                Err(e) => {
                    println!("Error opening GGUF file: {}", e);
                    process::exit(1);
                }
            };

            if let Err(e) = gguf.export_metadata(export_path) {
                println!("Error exporting metadata: {}", e);
                process::exit(1);
            }

            println!("Metadata exported successfully");
        }
        "import" => {
            if args.len() != 4 {
                println!("Invalid number of arguments for import command");
                print_usage();
                process::exit(1);
            }
            let file_path = &args[2];
            let import_path = &args[3];

            let mut gguf = match GGUFFile::new(file_path) {
                Ok(file) => file,
                Err(e) => {
                    println!("Error opening GGUF file: {}", e);
                    process::exit(1);
                }
            };

            if let Err(e) = gguf.import_metadata(import_path) {
                println!("Error importing metadata: {}", e);
                process::exit(1);
            }

            println!("Metadata imported successfully");
        }
        "search" => {
            if args.len() != 4 {
                println!("Invalid number of arguments for search command");
                print_usage();
                process::exit(1);
            }
            let file_path = &args[2];
            let search_key = &args[3];

            let gguf = match GGUFFile::new(file_path) {
                Ok(file) => file,
                Err(e) => {
                    println!("Error opening GGUF file: {}", e);
                    process::exit(1);
                }
            };

            let results = gguf.search_metadata(search_key);
            if results.is_empty() {
                println!("No matching metadata found");
            } else {
                println!("Matching metadata:");
                for metadata in results {
                    println!("Key: {}", metadata.key);
                    println!("Value: {}", metadata.value);
                    println!("Type: {}", metadata.value_type);
                    println!("---");
                }
            }
        }
        _ => {
            println!("Unknown command: {}", command);
            print_usage();
            process::exit(1);
        }
    }
}
