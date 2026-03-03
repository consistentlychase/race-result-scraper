import scraper
import weather



def main():
    scraper.get_race_ids()
    scraper.get_race_data()
    weather.get_weather()
    print("done, bitch")


if __name__ == "__main__":
    main()

