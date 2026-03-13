import base64
import json
import logging
import random
import requests
from seleniumbase import SB

# ---------------------------------------------------------
# Logging setup
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------
def get_geo_data():
    """Fetch geolocation data from ip-api with error handling."""
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        response.raise_for_status()
        data = response.json()
        return {
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "timezone": data.get("timezone"),
            "country_code": data.get("countryCode", "").lower()
        }
    except Exception as e:
        logging.error(f"Failed to fetch geo data: {e}")
        return None


def decode_username(encoded: str) -> str:
    """Decode base64 username safely."""
    try:
        return base64.b64decode(encoded).decode("utf-8")
    except Exception as e:
        logging.error(f"Failed to decode username: {e}")
        return None


# ---------------------------------------------------------
# Main automation logic
# ---------------------------------------------------------
def run_stream_viewer(proxy=None):
    geo = get_geo_data()
    if not geo:
        logging.error("Cannot continue without geo data.")
        return

    username = decode_username("YnJ1dGFsbGVz")
    if not username:
        logging.error("Cannot continue without username.")
        return

    url = f"https://www.twitch.tv/{username}"

    logging.info(f"Starting viewer for: {url}")

    while True:
        try:
            with SB(
                uc=True,
                locale="en",
                ad_block=True,
                chromium_arg="--disable-webgl",
                proxy=proxy
            ) as driver:

                rnd = random.randint(450, 800)

                driver.activate_cdp_mode(
                    url,
                    tzone=geo["timezone"],
                    geoloc=(geo["lat"], geo["lon"])
                )

                driver.sleep(2)

                # Cookie popups
                if driver.is_element_present('button:contains("Accept")'):
                    driver.cdp.click('button:contains("Accept")', timeout=4)

                driver.sleep(12)

                # Start watching
                if driver.is_element_present('button:contains("Start Watching")'):
                    driver.cdp.click('button:contains("Start Watching")', timeout=4)
                    driver.sleep(10)

                # Accept again if needed
                if driver.is_element_present('button:contains("Accept")'):
                    driver.cdp.click('button:contains("Accept")', timeout=4)

                # Check if live stream is present
                if driver.is_element_present("#live-channel-stream-information"):

                    # Open second viewer
                    driver2 = driver.get_new_driver(undetectable=True)
                    driver2.activate_cdp_mode(
                        'https://ffc.click/MHS3_Brutalles',
                        tzone=geo["timezone"],
                        geoloc=(geo["lat"], geo["lon"])
                    )
                    driver2.sleep(20)
                    driver2.cdp.open(url)
                    driver2.sleep(10)
                    if driver2.is_element_present('button:contains("Start Watching")'):
                        driver2.cdp.click('button:contains("Start Watching")', timeout=4)
                        driver2.sleep(10)

                    if driver2.is_element_present('button:contains("Accept")'):
                        driver2.cdp.click('button:contains("Accept")', timeout=4)

                    driver.sleep(rnd)

                else:
                    logging.info("Stream offline. Exiting loop.")
                    break

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            break


# ---------------------------------------------------------
# Test functions (safe, no browser automation)
# ---------------------------------------------------------
def test_geo_data():
    """Test that geo data returns expected structure."""
    data = get_geo_data()
    assert isinstance(data, dict), "Geo data must be a dict"
    assert "lat" in data and "lon" in data, "Missing coordinates"
    logging.info("test_geo_data passed.")


def test_username_decode():
    """Test base64 decoding."""
    decoded = decode_username("YnJ1dGFsbGVz")
    assert decoded == "brutalles", "Username decode mismatch"
    logging.info("test_username_decode passed.")


def test_url_format():
    """Test URL formatting logic."""
    username = "example"
    url = f"https://www.twitch.tv/{username}"
    assert url.startswith("https://"), "URL must be HTTPS"
    logging.info("test_url_format passed.")


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
if __name__ == "__main__":
    # Run tests (safe)
    test_geo_data()
    test_username_decode()
    test_url_format()

    # Run main script
    run_stream_viewer(proxy=None)
