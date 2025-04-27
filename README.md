# Speech Emotion Recognition (SER) Application

## Features

- **Speech Emotion Recognition**: Upload audio files or record audio directly to detect emotions
- **User Authentication**: Simple email-based authentication
- **Email Verification**: Email verification for account activation
- **Logging**: Comprehensive activity logging
- **Backup & Recovery**: Automated backup and restore functionality
- **Docker Support**: Containerized application for easy deployment

## Technical Implementation

### Security Features

- **Email Verification**: Account verification with email
- **Password Security**: Secure password hashing using Werkzeug
- **Input Validation**: Comprehensive form and input validation

### DevOps Capabilities

- **Docker Containerization**: Application packaged as Docker container
- **Docker Compose**: Multi-container orchestration for app, database, and backup
- **Automated Backups**: Daily backups of application data
- **Logging**: Comprehensive activity logging
- **Database Integration**: MongoDB integration for data persistence
- **Environment Configuration**: Configuration through environment variables

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the backend directory with the following variables:

```
# Flask Secret Key
SECRET_KEY=replace_with_a_secure_random_string

# MongoDB
MONGO_URI=mongodb://localhost:27017/SER

# Email (for sending verification emails)
# For Gmail, use App Password instead of account password
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your_app_password_here
```

### 3. Start MongoDB

Make sure MongoDB is running locally or update the MONGO_URI in your .env file.

### 4. Run the Application

```bash
python app.py
```

The application will be available at http://127.0.0.1:5000

## Troubleshooting

### Email Verification Link Issues

If clicking the email verification link results in an error:

1. Make sure you're using the same hostname (127.0.0.1) for both the application and verification link
2. Check your email server configuration

## Backup and Recovery

### Manual Backup

Run the following command to create a backup:

```
python backup.py backup
```

### Manual Restore

To restore from a backup:

```
python backup.py restore --file backups/backup_filename.zip
```

## Development

### Running Tests

```
pytest
```

### Code Structure

- `app.py`: Main application file
- `backup.py`: Backup and recovery utilities
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, and static assets

