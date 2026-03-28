# Formula 1 Social Network and Logging Website

This project is a web application that provides F1 fans with a space to share opinions and start discussions regarding F1 races.

## Features

- Create watchlists to keep all races you'd like to watch in one place
- Add ratings and reviews to any race from seasons 2023-2026
- View the general information regarding a race and its average rating on the race's dedicated page
- Interact with the community by replying to reviews
- View past race statistics for 2026 races to gain an understanding of the likelihood of certain events happening during the race
- View interactive data visualisations for a race of your choice to observe and analyse the race data
- Search for any race available and filter the results by year, driver win, team/constructor win, and race condition

## Technologies Used

- **HTML, CSS, JavaScript** for web application frontend
- **Flask** to handle app routing and user authentication
- **Bcrypt** for password hashing
- **Jinja2** to create templates for pages with similar contents/layouts, and display passed variables onto pages
- **WTForms** to simply form creation process
- **OpenF1 API** for F1 race data
- **Pandas** to clean up and filter dataframes holding data taken from API
- **Plotly** to create interactive visualisations
- **Dash** to create a dashboard for the visualisations

## Project Structure

```
project/
├── assets/
│   └── vis_style.css       # holds css code for dash visualisations app
├── dash_app/
│   └── visualisations.py   # dash app for F1 data visualisations
├── screenshots/            # screenshots of multiple pages from web app for README.md
│   ├── Screenshot1.png
│   ├── Screenshot2.png
│   ├── Screenshot3.png
│   ├── Screenshot4.png
│   ├── Screenshot5.png
│   ├── Screenshot6.png
│   └── Screenshot7.png
├── static/
│   ├── dashboard.css       # holds css code for user profile/dashboard page
│   ├── home_style.css      # holds css code for home.html
│   ├── race_style.css      # holds css code for all html files in all_seasons/
│   ├── results_style.css   # holds css code for search_results.html
│   ├── search_style.css    # holds css code for search.html
│   ├── seasons_style.css   # holds css code for seasons.html
│   ├── style.css           # holds css code for login.html and signup.html
│   └── wl_style.css        # holds css code for watchlist.html
├── tables/
│   ├── constructor_winners.csv  # contains F1 team win data from 2003 onwards
│   ├── f1_dataset_filtered.csv  # contains F1 driver win data from 2003 onwards
│   └── races_stats.csv          # contains F1 Grand Prix data from 2023 onwards
├── templates/
│   └── all_seasons/        # holds all html files for all races
│   │   ├── 2023/           # holds all html files for 2023 races
│   │   │   ├── abu_dhabi2023.html
│   │   │   ├── aus2023.html
│   │   │   └── ...
│   │   ├── 2024/           # holds all html files for 2024 races
│   │   │   ├── abu_dhabi2024.html
│   │   │   ├── aus2024.html
│   │   │   └── ...
│   │   ├── 2025/           # holds all html files for 2025 races
│   │   │   ├── abu_dhabi2025.html
│   │   │   ├── aus2025.html
│   │   │   └── ...
│   │   └── 2026/           # holds all html files for 2026 races
│   │       ├── abu_dhabi2026.html
│   │       ├── aus2026.html
│   │       └── ...
│   ├── home.html            # holds html code for home page
│   ├── login.html           # holds html code for login page
│   ├── race_template.html   # holds html code to be used by all race pages
│   ├── search_results.html  # holds html code for search results page
│   ├── search.html          # holds html code for search page
│   ├── seasons.html         # holds html code for all seasons page
│   ├── signup.html          # holds html code for sign up page
│   ├── user_dashboard.html  # holds html code for dashboard page
│   ├── watchlist.html       # holds html code for watchlist pages
│   └── wlist_template.html  # holds html code to be used by all watchlist pages
├── auth.py                  # holds flask app logic
├── data_filtering.py        # contains API calls and handles pandas df filtering
└── README.md                # markdown file that contains instructions on how to run the application
```

## API Disclaimer

As OpenF1 allows free access to all historical data and not live telemetry data, API queries are non-functional during F1 events (Free Practice/(Sprint) Qualifying/Grand Prix). This web app will work as normal around one hour after an F1 session has ended. The dates and times of each session can be found here: https://www.formula1.com/en/racing/2026

## Setup

1. Unzip file

2. Open terminal

3. Install dependencies

```bash
  pip install flask dash pandas plotly mysql-connector-python jinja2 bcrypt dash-bootstrap-components SQLAlchemy WTForms
```

4. Open project file in IDE of your choice

5. Run auth.py

6. Go to http://127.0.0.1:5000/

## Run Locally - Recreate Database (in case localhost cannot be reached)

1. Download mysql - https://www.mysql.com/downloads/

2. Using SQL Workbench/preferred database management tool, create 'users' database:

```bash
CREATE DATABASE `users` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
```

3. Unzip project file

4. Open terminal

5. Install dependencies

```bash
  pip install flask dash pandas plotly mysql-connector-python jinja2 bcrypt dash-bootstrap-components SQLAlchemy WTForms
```

5. Open project file in IDE of your choice

6. Adjust line 21 in auth.py to match your localhost settings:

```bash
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:[password]@localhost:[port number]/users"
```

7. Uncomment the following code on lines 532 and 533

```bash
    with app.app_context():
        db.create_all()
```

8. Run auth.py

9. Check that all tables defined in the db tables section of auth.py have successfully been added to database 'users'

10. Go to http://127.0.0.1:5000/ (the http link given in python terminal once you run the app)

## Screenshots

!['Lap Times' Histogram](./screenshots/Screenshot1.png)

!['Lap Times' Line Chart](./screenshots/Screenshot8.png)

**GUIDE:** Double-click on a colour in the 'Driver Number' key to view that single line. Click on other lines to add them to your filtered chart. Double-click again on the graph to view the original. Use the slider below to zoom in and view a specific section of the graph.

!['Qualifications and Race Results' Bar Chart](./screenshots/Screenshot2.png)

![Search Results Page](./screenshots/Screenshot3.png)

!['Past Race Stats' section of Japanese GP 2026 page](./screenshots/Screenshot4.png)

!['Add to which watchlist?' pop-up box](./screenshots/Screenshot5.png)

![Watchlist page example](./screenshots/Screenshot6.png)

![Reviews section example/Reviews section of 2024 British GP page](./screenshots/Screenshot7.png)

## License

[MIT](https://choosealicense.com/licenses/mit/)
