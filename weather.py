from typing import Any
import httpx
import logging
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import Response, JSONResponse, RedirectResponse
from dotenv import load_dotenv
import os
from sentry_config import init_sentry

load_dotenv()
init_sentry()

open_weather_api_key = os.getenv("OPEN_WEATHER_API_KEY")
assert open_weather_api_key, "OPEN_WEATHER_API_KEY is not set"

# Set up logger
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("weather", host="0.0.0.0", port=8000, streamable_http_path="/mcp")

# Constants
OPEN_WEATHER_API_BASE = "https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={open_weather_api_key}&units=imperial"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> list[dict[str, Any]] | dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling.

    Returns:
        - list[dict[str, Any]] for geocoding responses
        - dict[str, Any] for weather data responses
        - None if the request fails
    """
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Weather API request failed: {str(e)}")
            return None


async def get_lat_lon(city: str, state: str, country: str) -> tuple[float, float]:
    """Get the latitude and longitude for a city, state, and country."""
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{state},{country}&appid={open_weather_api_key}"
    data = await make_nws_request(url)
    if not data:
        logger.error(f"Failed to get location data for {city}, {state}, {country}")
        raise ValueError("Could not get location data")
    return float(data[0]["lat"]), float(data[0]["lon"])


@mcp.tool()
async def get_current_weather(city: str, state: str, country: str) -> str:
    """
    Get the current weather for a location. If the city, state, or country are not provided, a reasonable guess should
    be made as to what the user is asking for.
    """
    logger.info(f"Weather request for {city}, {state}, {country}")

    try:
        # Get coordinates and weather data
        lat, lon = await get_lat_lon(city, state, country)
        points_data = await make_nws_request(
            OPEN_WEATHER_API_BASE.format(
                lat=lat, lon=lon, open_weather_api_key=open_weather_api_key
            )
        )

        if not points_data:
            return "Unable to fetch forecast data for this location."

        # Extract weather data
        weather_main = points_data["weather"][0]["main"]
        weather_description = points_data["weather"][0]["description"]
        weather_temp = points_data["main"]["temp"]
        weather_feels_like = points_data["main"]["feels_like"]
        weather_humidity = points_data["main"]["humidity"]

        return f"The current weather is {weather_main} with a description of {weather_description}. The temperature is {weather_temp} degrees Fahrenheit. The feels like temperature is {weather_feels_like} degrees Fahrenheit. The humidity is {weather_humidity}%."

    except Exception as e:
        # Log any exceptions as errors
        logger.error(f"Error getting weather for {city}, {state}, {country}: {str(e)}")
        return f"Sorry, I encountered an error while fetching weather data for {city}."


@mcp.custom_route("/", methods=["GET"])
async def redirect_to_github(request: Request) -> Response:
    return RedirectResponse(
        url="https://github.com/mcp-getgather/api-weather-mcp",
        status_code=301,
    )


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> Response:
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    logger.info("Starting weather MCP server")
    try:
        mcp.run(transport="streamable-http")
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise
