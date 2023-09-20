# Earthquake Relief Map

This is a web application for tracking earthquake relief efforts and coordinating aid distribution. The application allows volunteers to submit information about the type of vehicle, type of aid, and location using GPS coordinates.

## Project Structure

- `static/`: Contains static files (CSS and JavaScript).
  - `css/`: CSS stylesheets for web pages.
  - `js/`: JavaScript files (optional).

- `templates/`: HTML templates for the web application.
  - `index.html`: Main page with a form for submitting information.
  - `map.html`: Page for displaying the interactive map (customize based on your chosen mapping library).

- `app.py`: The Flask application with routes for handling form submissions.

- `requirements.txt`: List of Python dependencies required for the project.

## Getting Started

1. Install the required dependencies listed in `requirements.txt`.

2. Run the Flask application by executing `app.py`.

3. Access the application in your web browser.

## Usage

- Users can fill out the form on the main page to submit information about aid efforts.

- The interactive map page (map.html) displays aid distribution based on user submissions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
