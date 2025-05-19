# Web Methods to SnapLogic Migration Accelerator

A Streamlit web application that facilitates migrating integrations from Web Methods to SnapLogic by analyzing ZIP packages and providing conversion recommendations.

## Features

- Upload Web Methods ZIP packages for analysis
- Configure migration settings
- Visualize conversion metrics
- Generate and download SnapLogic pipeline equivalents

## Setup and Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure backend API endpoint in `config.py`
4. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. Launch the application
2. Upload your Web Methods ZIP package
3. Configure migration settings
4. Click "Start Migration Process"
5. Review results and download SnapLogic pipelines

## Configuration

You can customize the application behavior by editing the `config.py` file:

- `API_ENDPOINT`: URL for the backend processing API
- `MAX_UPLOAD_SIZE_MB`: Maximum allowed file size
- `SUPPORTED_FILE_TYPES`: List of supported file extensions
- Feature flags for different migration options

## Requirements

- Python 3.7+
- Streamlit 1.32.0+
- Requests 2.31.0+

## Support

For support or questions, please contact your migration team. 