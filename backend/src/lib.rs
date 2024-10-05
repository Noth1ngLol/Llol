use std::fs::File;
use std::io::{Read, Write, Seek, SeekFrom};
use std::path::Path;
use serde::{Serialize, Deserialize};
use serde_json::Value;
use byteorder::{LittleEndian, ReadBytesExt, WriteBytesExt};

#[derive(Debug, Serialize, Deserialize)]
pub struct GGUFMetadata {
    pub key: String,
    pub value: Value,
    pub value_type: String,
}

pub struct GGUFFile {
    path: String,
    metadata: Vec<GGUFMetadata>,
}

impl GGUFFile {
    pub fn new(path: &str) -> Result<Self, std::io::Error> {
        let mut file = File::open(path)?;
        let metadata = Self::read_metadata(&mut file)?;
        Ok(Self {
            path: path.to_string(),
            metadata,
        })
    }

    fn read_metadata(file: &mut File) -> Result<Vec<GGUFMetadata>, std::io::Error> {
        file.seek(SeekFrom::Start(0))?;
        let mut magic = [0u8; 4];
        file.read_exact(&mut magic)?;
        if &magic != b"GGUF" {
            return Err(std::io::Error::new(std::io::ErrorKind::InvalidData, "Not a valid GGUF file"));
        }
        
        let version = file.read_u32::<LittleEndian>()?;
        let _tensor_count = file.read_u64::<LittleEndian>()?;
        let metadata_count = file.read_u64::<LittleEndian>()? as usize;
        
        let mut metadata = Vec::with_capacity(metadata_count);
        for _ in 0..metadata_count {
            let key_length = file.read_u64::<LittleEndian>()? as usize;
            let mut key = vec![0u8; key_length];
            file.read_exact(&mut key)?;
            let key = String::from_utf8_lossy(&key).to_string();
            
            let value_type = file.read_u32::<LittleEndian>()?;
            let value = match value_type {
                0 => Value::Null,
                1 => Value::Bool(file.read_u8()? != 0),
                2 => Value::Number(file.read_i64::<LittleEndian>()?.into()),
                3 => Value::Number(file.read_f64::<LittleEndian>()?.into()),
                4 => {
                    let str_length = file.read_u64::<LittleEndian>()? as usize;
                    let mut str_value = vec![0u8; str_length];
                    file.read_exact(&mut str_value)?;
                    Value::String(String::from_utf8_lossy(&str_value).to_string())
                },
                _ => return Err(std::io::Error::new(std::io::ErrorKind::InvalidData, "Unknown value type")),
            };
            
            metadata.push(GGUFMetadata {
                key,
                value,
                value_type: value_type.to_string(),
            });
        }
        
        Ok(metadata)
    }

    pub fn modify_metadata(&mut self, key: &str, value: Value, value_type: &str) -> Result<(), std::io::Error> {
        if let Some(metadata) = self.metadata.iter_mut().find(|m| m.key == key) {
            metadata.value = value;
            metadata.value_type = value_type.to_string();
        } else {
            self.metadata.push(GGUFMetadata {
                key: key.to_string(),
                value,
                value_type: value_type.to_string(),
            });
        }
        self.save()
    }

    pub fn remove_metadata(&mut self, key: &str) -> Result<(), std::io::Error> {
        self.metadata.retain(|m| m.key != key);
        self.save()
    }

    pub fn save(&self) -> Result<(), std::io::Error> {
        let mut file = File::create(&self.path)?;
        
        file.write_all(b"GGUF")?;
        file.write_u32::<LittleEndian>(1)?;
        file.write_u64::<LittleEndian>(0)?;
        file.write_u64::<LittleEndian>(self.metadata.len() as u64)?;
        
        for metadata in &self.metadata {
            file.write_u64::<LittleEndian>(metadata.key.len() as u64)?;
            file.write_all(metadata.key.as_bytes())?;
            
            match metadata.value {
                Value::Null => {
                    file.write_u32::<LittleEndian>(0)?;
                },
                Value::Bool(b) => {
                    file.write_u32::<LittleEndian>(1)?;
                    file.write_u8(b as u8)?;
                },
                Value::Number(n) => {
                    if n.is_i64() {
                        file.write_u32::<LittleEndian>(2)?;
                        file.write_i64::<LittleEndian>(n.as_i64().unwrap())?;
                    } else {
                        file.write_u32::<LittleEndian>(3)?;
                        file.write_f64::<LittleEndian>(n.as_f64().unwrap())?;
                    }
                },
                Value::String(s) => {
                    file.write_u32::<LittleEndian>(4)?;
                    file.write_u64::<LittleEndian>(s.len() as u64)?;
                    file.write_all(s.as_bytes())?;
                },
                _ => return Err(std::io::Error::new(std::io::ErrorKind::InvalidData, "Unsupported value type")),
            }
        }
        
        Ok(())
    }

    pub fn export_metadata(&self, export_path: &str) -> Result<(), std::io::Error> {
        let json = serde_json::to_string_pretty(&self.metadata)?;
        let mut file = File::create(export_path)?;
        file.write_all(json.as_bytes())?;
        Ok(())
    }

    pub fn import_metadata(&mut self, import_path: &str) -> Result<(), std::io::Error> {
        let mut file = File::open(import_path)?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;
        self.metadata = serde_json::from_str(&contents)?;
        self.save()
    }

    pub fn search_metadata(&self, search_key: &str) -> Vec<&GGUFMetadata> {
        self.metadata.iter().filter(|m| m.key.contains(search_key)).collect()
    }
}
