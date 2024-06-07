from python_weather import Client, METRIC

from bot import SubBot


class WeatherBot(SubBot):
    def __init__(self, location: str):
        self.location = location
        
    def get_current_mood(self):
        return self.weather.current.description.lower()
    
    def get_low_bound(self):
        return self.today_forecast.lowest_temperature
    
    def get_high_bound(self):
        return self.today_forecast.highest_temperature
    
    async def get_msg(self, scheduled):
        print("Getting client")
        async with Client(unit=METRIC) as client:
            print("got client")
            self.weather = await client.get(self.location)
            print("Getting weather")
            self.today_forecast = next(self.weather.forecasts)
            return f'''
                Here is your weather report for {self.location}:
            The current weather is overall {self.get_current_mood()}.
            Today's temperature range from {self.get_low_bound()} Celsius to {self.get_high_bound()} Celsius.
                '''