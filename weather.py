from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import Response, JSONResponse, RedirectResponse
from dotenv import load_dotenv
import os

load_dotenv()

open_weather_api_key = os.getenv("OPEN_WEATHER_API_KEY")
assert open_weather_api_key, "OPEN_WEATHER_API_KEY is not set"

# Initialize FastMCP server
mcp = FastMCP("weather", host="0.0.0.0", port=8000, streamable_http_path="/mcp")

lat = 40.7606
lon = -111.8910

# Constants
OPEN_WEATHER_API_BASE = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={open_weather_api_key}&units=imperial"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


@mcp.tool()
async def get_current_weather() -> str:
    """Get the current weather for a location."""
    # First get the forecast grid endpoint
    points_data = await make_nws_request(OPEN_WEATHER_API_BASE)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    weather_main = points_data["weather"][0]["main"]
    weather_description = points_data["weather"][0]["description"]
    weather_temp = points_data["main"]["temp"]
    weather_feels_like = points_data["main"]["feels_like"]
    weather_temp_min = points_data["main"]["temp_min"]
    weather_temp_max = points_data["main"]["temp_max"]
    weather_humidity = points_data["main"]["humidity"]

    return f"The current weather is {weather_main} with a description of {weather_description}. The temperature is {weather_temp} degrees Fahrenheit. The feels like temperature is {weather_feels_like} degrees Fahrenheit. The temperature minimum is {weather_temp_min} degrees Fahrenheit. The temperature maximum is {weather_temp_max} degrees Fahrenheit. The humidity is {weather_humidity}%."


@mcp.custom_route("/", methods=["GET"])
async def redirect_to_github(request: Request) -> Response:
    return RedirectResponse(
        url="https://github.com/mcp-getgather/containerized-weather-mcp",
        status_code=301,
    )


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> Response:
    return JSONResponse({"status": "ok"})


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="streamable-http")
