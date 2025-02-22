# Project Structure

## Directory Layout

### Documentation (/docs)
- Design documents and architecture
- Technical specifications
- Project planning materials

### Frontend (/frontend)
- React components for UI
- Next.js page routing
- Static assets and resources
- Styling and CSS modules
- Frontend utility functions

### Backend (/backend)
- API Layer
  - Version 1 endpoints
  - API middleware
- Core Logic
  - Swing analysis implementation
  - Video processing systems
- Data Models
  - Domain model definitions
  - Pydantic schema validation
- External Services Integration

### Machine Learning (/ml)
- Pose estimation implementation
- Swing analysis algorithms
- ML utility functions

### Testing (/tests)
- Unit test suites
- Integration tests
- End-to-end testing

### Infrastructure
- Setup and deployment scripts
- GitHub Actions workflows
- Docker configurations
- Python dependency management
  - Base requirements
  - Development dependencies
  - Production dependencies

### Configuration
- Environment variable templates
- Docker Compose setup
- Python project settings

## Key Components

### Frontend Components
- **components/**: Reusable React components
- **pages/**: Next.js pages and routing
- **public/**: Static assets and resources
- **styles/**: Global styles and CSS modules
- **utils/**: Frontend utility functions

### Backend Components
- **api/**: API endpoint definitions and routing
- **core/**: Core business logic implementation
- **models/**: Data models and schemas
- **services/**: External service integrations

### ML Components
- **pose/**: Pose estimation model implementation
- **analysis/**: Swing analysis algorithms
- **utils/**: ML utility functions and helpers

### Supporting Components
- **tests/**: Comprehensive test suite
- **scripts/**: Utility and automation scripts
- **docker/**: Container configurations
- **requirements/**: Dependency management

## Development Guidelines

### Frontend Development
- Follow component-based architecture
- Use TypeScript for type safety
- Implement responsive design
- Follow Next.js best practices

### Backend Development
- Follow RESTful API design principles
- Use FastAPI dependency injection
- Implement proper error handling
- Follow Python type hints

### ML Development
- Version control model artifacts
- Document model parameters
- Track experiment results
- Follow ML ops best practices

### Testing
- Write unit tests for all components
- Implement integration tests
- Perform end-to-end testing
- Maintain test coverage
