# ladders-app

## Overview

Welcome to our CIS 189 final project! We've utilized a CP solver to create ladders, an automatic matching web app that pairs people up for meet ups based on their preferences efficiently. It saves people's preferences as well as previous pairings, and when matching provides a dashboard to analyze which preferences weren't met.
NOTE: Originally we planned to have a log in feature to edit preferences, but unfortunately we decided it required a significant of additional complexity and its functionality has been removed.

## File Structure

### Backend

The `backend` folder contains the code that produces the matches and runs the server allowing for communication between the frontend and the stored data (which is stored in the form of `.txt` files). The file `matcher.py` contains our implementation of `LaddersMatcher`, which provides the functionality for reading in preference data, creating variables and constraints, and solving the problem and outputting the solution. The file `server.py` contains the code for the Flask server which instantiates an instance of `LaddersMatcher` and implements API endpoints. Finally, `people.txt` stores profile and preference data, and `previous-matches.txt` stores data on previous matches. If we were to actually implement and deploy this project, we would probably have to use a full-on DB, but these files allow for local storage for the sake of our project.

### Frontend

The `frontend` folder contains all the code for the React app behind the frontend for our project. Outside of the boilerplate, all of our pages/components are contained in the `components` folder. For example, `Dashboard.js` contains all the code for the `/dashboard` page. Other pages include Home and Account which use other components like singup and textfield. It also contains various .css files for different styles.

## Running our App

For the backend, make sure you have the latest versions of `ortools` and `flask` installed with your version of python. From the root directory, open a terminal window and navigate to the `backend` directory, then run `server.py` as follows:

```
cd backend
python3 server.py
```

Now, open a new terminal window and, from the root directory, navigate to the `frontend` directory and start the React app as follows (before starting the app, don't forget to do an `npm install` if you haven't already):

```
cd frontend
npm start
```

The main page of our app should now be running at `localhost:3000`. You can find the dashboard that allows for visualizing matches at `localhost:3000/dashboard`.
