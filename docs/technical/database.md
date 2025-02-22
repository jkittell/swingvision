# SwingVision Database Design

## CrateDB Schema

### Users Table
- **Primary Key**: Unique string identifier
- **Core Fields**:
  - Username
  - Email address
  - Creation timestamp
  - Last update timestamp
- **Extended Data**:
  - Dynamic settings object

### Videos Table
- **Primary Key**: Unique string identifier
- **Relationships**:
  - User ID reference
- **Core Fields**:
  - Filename
  - Upload timestamp
  - Duration in seconds
  - Processing status
- **Extended Data**:
  - Dynamic metadata
  - Blob storage reference

### Poses Table
- **Primary Key**: Unique string identifier
- **Relationships**:
  - Video ID reference
- **Temporal Data**:
  - Frame number
  - Timestamp
- **Analysis Data**:
  - Dynamic keypoints array
  - Confidence score
  - Similarity search vector

### Swing Analysis Table
- **Primary Key**: Unique string identifier
- **Relationships**:
  - Video ID reference
  - User ID reference
- **Core Fields**:
  - Analysis timestamp
  - Overall score
- **Extended Data**:
  - Dynamic metrics object
  - Dynamic feedback array

### Progress Table
- **Primary Key**: Unique string identifier
- **Relationships**:
  - User ID reference
- **Core Fields**:
  - Progress date
- **Extended Data**:
  - Dynamic metrics object
- **Optimization**:
  - B-tree index on date
  - 6-shard clustering

## Data Types

### Pose Keypoints Structure
- Array of body point measurements
- Each keypoint contains:
  - Descriptive name (e.g., left_shoulder)
  - 3D coordinates (x, y, z)
  - Confidence score for accuracy

### Swing Metrics Structure
- Key measurements include:
  - Head movement stability
  - Hip rotation angle
  - Shoulder turn angle
  - Swing plane angle
  - Swing tempo ratio

### Feedback Structure
- Analysis components:
  - Target aspect (e.g., shoulder_turn)
  - Observational findings
  - Improvement recommendations
  - Priority ranking

## Indexing Strategy

- Vector indexing for pose similarity search
- B-tree indexes on frequently queried fields
- Timestamp indexing for time-series data
- Sharding based on user_id

## Data Retention

- Raw videos: 30 days
- Processed data: indefinite
- Analysis results: indefinite
- Progress data: indefinite

## Backup Strategy

- Regular snapshots
- Incremental backups
- Cross-region replication
- Point-in-time recovery capability
