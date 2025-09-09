from podcast.creator import PodcastCreator
from podcast.utilities.bundle import UtilitiesBundle


def main() -> None:
    """
    The main function that initializes the UtilitiesBundle, sets date ranges, and
    orchestrates the podcast generation process.
    """
    utilities = UtilitiesBundle()

    # Get the current time and calculate a date range for the past 7 days.
    max_date = utilities.time.current_time
    min_date = utilities.time.get_time_offset(days=7)

    # Instantiate PodcastCreator with specific query and sources (biorxiv and pubmed)
    podcast_creator = PodcastCreator(
        query="biological imaging OR bioimaging OR microscopy OR live-cell imaging OR fluorescence microscopy OR cryo-EM OR super-resolution microscopy OR light sheet microscopy OR electron microscopy OR multiphoton imaging",  # Query term for article search
        utilities=utilities,  # Utilities bundle for configurations, logging, etc.
        path="test/",  # Path for saving podcast files
        arxiv=False,  # Disable arXiv source
        biorxiv=True,  # Enable biorxiv source
        pubmed=True,  # Enable PubMed source
        min_date=min_date,  # Set minimum date for the search range
        max_date=max_date,  # Set maximum date (current time)
        max_results=25,  # Maximum number of articles to retrieve
    )

    # Generate the podcast episode(s) based on the provided strategies and configurations
    podcast_creator.generate_podcast()


if __name__ == "__main__":
    main()
