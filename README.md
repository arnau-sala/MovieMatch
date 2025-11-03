# 🎬 MovieMatch - Discover Your Next Favorite Movie

![MovieMatch](https://img.shields.io/badge/MovieMatch-v1.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![TMDB](https://img.shields.io/badge/TMDB-API-yellow.svg)

MovieMatch is an interactive web application developed with Streamlit that helps you discover perfect movies using the powerful API from The Movie Database (TMDB). With an intelligent recommendation system and a user-friendly interface, finding your next favorite movie has never been easier.

## ✨ Main Features

### 🔍 Advanced Search
- **Search by title**: Find specific movies by name
- **Detailed results**: Complete information with posters, synopsis, ratings, and more
- **Smart filtering**: Filter by popularity and release date

### 🎯 Personalized Recommendations System
- **For You section**: Intelligent recommendations based on your profile
- **Profile-based patterns**: Automatic analysis of your preferences including:
  - Favorite directors
  - Preferred actors
  - Favorite genres
  - Production countries
  - Production companies
  - Original languages
- **Daily updates**: Recommendations are recalculated daily based on your interactions

### 📊 Content Exploration
- **Popular Movies**: The most popular movies right now
- **Top Rated**: Classic and critically acclaimed films
- **Now Playing**: Current releases in theaters
- **Coming Soon**: Upcoming movie releases
- **By Genre**: Filter movies by genre
- **Random Pick**: Discover a random movie
- **Movie of the Day**: A featured movie that changes daily

### 👤 User Profile
- **Favorite Genres**: Select your preferred movie genres
- **Movie Ratings**: Rate movies you've watched
- **Search History**: Your searches are automatically saved to improve recommendations
- **Privacy-First**: All data is stored locally and anonymously

## 🚀 Installation and Setup

### Prerequisites
- Python 3.8 or higher
- Account on [The Movie Database (TMDB)](https://www.themoviedb.org/)
- TMDB API Key (free)

### 1. Clone the Repository
```bash
git clone https://github.com/arnau-sala/MovieMatch.git
cd MovieMatch
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv moviematch_env

# On Windows
moviematch_env\Scripts\activate

# On macOS/Linux
source moviematch_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure TMDB API Key

#### Get your API Key:
1. Sign up at [TMDB](https://www.themoviedb.org/signup)
2. Go to your profile → Settings → API
3. Request an API Key (it's free and approved immediately)

#### Configure the key:
Create a `.env` file in the project root directory:

```env
TMDB_API_KEY=your_api_key_here
```

**Important!** Never share your API key publicly or commit it to repositories.

### 5. Run the Application

#### Local Development
```bash
streamlit run app.py
```

The application will automatically open in your browser at `http://localhost:8501`

#### Deploy to Web (Make it Publicly Accessible)

To make your app accessible from any browser without downloading the code, you can deploy it to a hosting service:

##### Option 1: Streamlit Cloud (Recommended - Free & Easy)

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository and branch
6. Set the main file path to `app.py`
7. Add your `TMDB_API_KEY` as a secret in the app settings
8. Click "Deploy" - your app will be live at `https://your-app-name.streamlit.app`

**Benefits:**
- ✅ Free hosting
- ✅ Automatic deployments on git push
- ✅ Easy setup (5 minutes)
- ✅ No server management needed

##### Option 2: Other Hosting Options

- **Heroku**: Deploy with a `Procfile` and `requirements.txt`
- **AWS/GCP/Azure**: Use container services or serverless options
- **DigitalOcean/Railway**: Simple deployment platforms
- **Self-hosted**: Run on your own server with `streamlit run app.py --server.address=0.0.0.0 --server.port=8501`

## 📱 Usage Guide

### Main Navigation
The application has 7 main sections accessible from the navigation buttons:

1. **Popular Movies**
   - Discover the most popular movies right now
   - Automatically updated according to TMDB trends

2. **Now Playing**
   - Movies currently in theaters
   - Stay up to date with current releases

3. **Top Rated**
   - Explore movies with the best ratings
   - Classic and critically acclaimed films

4. **Coming Soon**
   - Upcoming movies to be released
   - Plan your future cinema visits

5. **By Genre**
   - Filter movies by genre
   - Select from 12 popular genres

6. **For You**
   - Personalized recommendations based on your profile
   - Analyzes your searches, ratings, and preferences
   - Updated daily

7. **Random Pick**
   - Discover a random movie
   - Perfect when you don't know what to watch

### Profile Section
Access your profile from the top-right corner to:
- Select your favorite genres
- Rate movies you've watched
- View your watched movies list
- Read the privacy policy

### How Recommendations Work
The "For You" section analyzes:
- Your search history
- Your movie ratings
- Your favorite genres
- Patterns in directors, actors, genres, countries, companies, and languages you prefer

Based on this data, it generates personalized recommendations that are updated daily.

## 🛠️ Project Structure

```
MovieMatch/
│
├── app.py                 # Main Streamlit application
├── utils.py              # TMDB client and utility functions
├── recommendations.py    # Recommendation system
├── user_utils.py        # User ID and profile management
├── movie_display.py     # Movie display components
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template (create .env manually)
├── README.md           # Project documentation
└── .gitignore         # Git ignore file
```

## 🔧 Technologies Used

- **[Streamlit](https://streamlit.io/)**: Web framework for data applications
- **[TMDB API](https://developers.themoviedb.org/3)**: Movie database API
- **[Requests](https://requests.readthedocs.io/)**: HTTP client for Python
- **[Python-dotenv](https://pypi.org/project/python-dotenv/)**: Environment variable management
- **[Pandas](https://pandas.pydata.org/)**: Data manipulation
- **[Streamlit JS Eval](https://pypi.org/project/streamlit-js-eval/)**: JavaScript evaluation for localStorage

## 🎨 Interface Features

- **Responsive Design**: Works perfectly on desktop and mobile
- **Interactive Cards**: Information organized in visual cards
- **Optimized Images**: High-quality posters from TMDB
- **Intuitive Navigation**: Easy-to-use navigation buttons
- **Visual Feedback**: Loading spinners and status messages
- **Custom Styling**: Integrated CSS for a better experience
- **Dark Theme**: Professional dark theme with Poppins font

## 🔒 Privacy

MovieMatch is designed with privacy in mind:
- **Anonymous**: All data is stored with a random 4-character alphanumeric ID
- **Local Storage**: All data is stored locally in `user_data.json`
- **No Tracking**: No third-party services, trackers, or advertising
- **No Account Required**: No login or registration needed
- **User Control**: You can delete your data at any time

See the Privacy Policy in the Profile section for complete details.

## 🤝 Contributing

Contributions are welcome! If you want to improve MovieMatch:

1. **Fork** the repository
2. Create a **feature branch** (`git checkout -b feature/new-feature`)
3. **Commit** your changes (`git commit -m 'Add new feature'`)
4. **Push** to the branch (`git push origin feature/new-feature`)
5. Open a **Pull Request**

### Ideas for Contributing
- [ ] Add support for TV series
- [ ] Implement local favorites system
- [ ] Add more streaming providers
- [ ] Improve recommendation algorithms
- [ ] Add internationalization (i18n)
- [ ] Add movie watchlists

## 📝 License

This project is licensed under the **MIT License** - a free and open-source license with no restrictions.

### What this means:
- ✅ **Free to use** - Commercial and private use allowed
- ✅ **Free to modify** - Change the code as you wish
- ✅ **Free to distribute** - Share and redistribute freely
- ✅ **Free to sublicense** - Include in your own projects
- ✅ **No restrictions** - No limitations on use or modification

The only requirement is to include the copyright notice and license text when redistributing.

See the [LICENSE](LICENSE) file for the full license text.

## 🙏 Acknowledgments

- **[The Movie Database (TMDB)](https://www.themoviedb.org/)** for providing the free API
- **[Streamlit](https://streamlit.io/)** for the excellent web framework
- **Developer community** for feedback and contributions

## 📞 Support and Contact

If you have questions, suggestions, or find any issues:

- 🐛 **Report bugs**: [Open an issue](https://github.com/arnau-sala/MovieMatch/issues/new)
- 💡 **Suggest improvements**: [Open an issue](https://github.com/arnau-sala/MovieMatch/issues/new)
- 📧 **Direct contact**: arnausalaaraujo@gmail.com

## 🚀 Future Versions

### v1.1 (Coming Soon)
- [ ] Support for multiple languages
- [ ] Refine AI recommendation system
- [ ] Enhanced streaming provider integration

### v1.2 (Planned)
- [ ] TV series support
- [ ] Social features (share recommendations)
- [ ] Advanced filtering options

---

**Enjoy discovering your next favorite movie with MovieMatch! 🍿🎬**
