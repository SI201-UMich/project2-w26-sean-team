# SI 201 HW4 (Library Checkout System)
# Your name: Sean Manoff
# Your student id: 95152984
# Your email: smanoff@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    infile = open(html_path, "r", encoding="utf-8-sig")
    data = infile.read()
    infile.close()
    soup = BeautifulSoup(data, "html.parser")
    all_links = soup.find_all("a")
    listing_info = []
    ids = []

    for link in all_links:
        href = link.get("href")
        if href != None:
            if "/rooms/" in href:
                pieces = href.split("/rooms/")
                if len(pieces) > 1:
                    id_piece = pieces[1]
                    if "?" in id_piece:
                        listing_id = id_piece.split("?")[0]
                    else:
                        listing_id = id_piece
                    if "/" in listing_id:
                        listing_id = listing_id.split("/")[-1]
                
                    tag = soup.find(id="title_" + listing_id)
                    if tag != None:
                        listing_title = tag.get_text().strip()
                    if listing_title != "" and listing_id not in ids:
                        listing_info.append((listing_title, listing_id))
                        ids.append(listing_id)
    return listing_info


    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    filename = "html_files/listing_" + listing_id + ".html"
    infile = open(filename, "r", encoding="utf-8-sig")
    data = infile.read()
    infile.close()

    soup = BeautifulSoup(data, "html.parser")
    text = soup.get_text(" ")

    policy_number = ""
    li_tags = soup.find_all("li")
    for li in li_tags:
        li_text = li.get_text()
        if "Policy number" in li_text:
            parts = li_text.split(":")
            if len(parts) > 1:
                policy_number = parts[1].strip()

    if policy_number == "":
        if "Policy number:" in text:
            pieces = text.split("Policy number:")
            if len(pieces) > 1:
                remaining = pieces[1]
                policy_number = remaining.split()[0]

    if policy_number == "":
        policy_number = "Exempt"
    elif "pending" in policy_number.lower():
        policy_number = "Pending"
    elif "exempt" in policy_number.lower():
        policy_number = "Exempt"

    if "Superhost" in text:
        host_type = "Superhost"
    else:
        host_type = "regular"

    host_name = ""
    h2_tags = soup.find_all("h2")
    for h2 in h2_tags:
        t = h2.get_text()
        if "Hosted by" in t:
            host_name = t.replace("Hosted by", "").strip()

    if host_name == "":
        if "Hosted by " in text:
            pieces = text.split("Hosted by ")
            if len(pieces) > 1:
                host_piece = pieces[1]
                if "Joined" in host_piece:
                    host_name = host_piece.split("Joined")[0].strip()
                else:
                    host_name = host_piece.split()[0].strip()

    room_type = "Entire Room"
    line = ""
    for h2 in h2_tags:
        t = h2.get_text()
        if "hosted by" in t.lower():
            line = t

    if line == "":
        line = text

    if "Private" in line:
        room_type = "Private Room"
    elif "Shared" in line:
        room_type = "Shared Room"

    location_rating = 0.0
    matches = re.findall(r'Location</div><div class="_bgq2leu"><div class="_7pay" aria-label="([0-9.]+) out of 5\.0"', data)
    if len(matches) > 0:
        location_rating = float(matches[0])

    return {listing_id: {"policy_number": policy_number, "host_type": host_type, "host_name": host_name, "room_type": room_type, "location_rating": location_rating}}


    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    listing_results = load_listing_results(html_path)
    detailed_data = []
    for listing in listing_results:
        listing_title = listing[0]
        listing_id = listing[1]
        details = get_listing_details(listing_id)
        l = details[listing_id]
        row = (listing_title, listing_id, l["policy_number"], l["host_type"], l["host_name"], l["room_type"], l["location_rating"])
        detailed_data.append(row)
    return detailed_data
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    outfile = open(filename, "w", newline="")
    writer = csv.writer(outfile)

    writer.writerow(["Listing Title", "Listing ID", "Policy Number", "Host Type", "Host Name", "Room Type", "Location Rating"])

    ds = sorted(data, key=lambda x: x[6], reverse=True)
    for row in ds:
        writer.writerow(row)
    outfile.close()
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        self.assertEqual(len(self.listings), 18)
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.
        final = []
        for listing_id in html_list:
            final.append(get_listing_details(listing_id))

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        self.assertEqual(final[0]["467507"]["policy_number"], "STR-0005349")
        self.assertEqual(final[2]["1944564"]["host_type"], "Superhost")
        self.assertEqual(final[2]["1944564"]["room_type"], "Entire Room")
        self.assertAlmostEqual(final[2]["1944564"]["location_rating"], 4.9)

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
        for row in self.detailed_data:
            self.assertEqual(len(row), 7)
        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        self.assertEqual(self.detailed_data[-1], ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8))

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")
        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        output_csv(self.detailed_data, out_path)
        # TODO: Read the CSV back in and store rows in a list.
        infile = open(out_path, "r")
        r = csv.reader(infile)
        rows = []

        for row in r:
            rows.append(row)
        infile.close()
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].
        self.assertEqual(rows[1], ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"])
        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        pass

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        pass


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)