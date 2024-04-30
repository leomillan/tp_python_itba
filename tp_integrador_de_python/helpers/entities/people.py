"""File with the people entities class"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .base_entity import BaseEntity
from .exceptions import AssignIDError, MissingColumnsError, MissingPersonError


class People(BaseEntity):

    def __init__(
        self, name: int, year: int, gender: str, zipcode: str, idx: int = None
    ):
        self.name = name
        self.year = year
        self.gender = gender
        self.zipcode = zipcode
        self.idx = idx

    def __repr__(self) -> str:
        """Prints movies information"""
        return f"name = {self.name} \nyear = {self.year} \ngender = {self.gender} \nzipcode = {self.zipcode} \nidx = {self.idx}"

    def write_df(self, df: pd.DataFrame):
        """Function to write the current person in the dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with people information.

        Raises
        ------
        ValueError
            If the idx is already assigned.
        """

        if self.idx:
            raise AssignIDError("This person has an id already assigned")

        new_id = df["id"].max() + 1
        new_index = len(df.index)
        df.loc[
            new_index, ["id", "Full Name", "year of birth", "Gender", "Zip Code"]
        ] = [new_id, self.name, self.year, self.gender, self.zipcode]
        self.idx = new_id
        print(f"The person '{self.name}' was added to the dataframe with id {self.idx}")

    @classmethod
    def get_from_df(
        cls,
        df: pd.DataFrame,
        idx: int | list = None,
        name: str | list = None,
        year: list[int] = None,
        gender: str | list = None,
        zipcode: str | list = None,
    ) -> list:
        """Class method to filter people from a dataframe given the idx, name, year, gender or zipcode

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the people information.
        idx : int | list, Default None
            Index or list of index to filter.
        name : str | list, Default None
            Movie name or list of names to filter.
        year : list[int], Default None
            List with two years range to filter.
        gender : str, Default None
            Gender to filter by.
        zipcode : str | list, Default None
            Zipcode or list of zipcodes to filter.

        Returns
        -------
        list[People]
            List of People class instances that match the filters conditions.

        """
        people_list = []
        filtered = cls._filter(
            df, year=year, gender=gender, zipcode=zipcode, name=name, idx=idx
        )

        if not filtered.empty:
            for index, row in filtered.iterrows():
                people_list.append(
                    People(
                        name=row["Full Name"],
                        year=row["year of birth"],
                        gender=gender,
                        zipcode=row["Zip Code"],
                        idx=row["id"],
                    )
                )
        return people_list

    def remove_from_df(self, df):
        """Function to delete the curring person from the given dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the people information.

        Raises
        ------
        MissingPersonError
            Raises if the person is not found in the dataframe.
        """
        filtered = df[(df["Gender"] == self.gender)]
        filtered = filtered[
            (filtered["Full Name"] == self.name)
            & (filtered["year of birth"] == self.year)
            & (filtered["id"] == self.idx)
            & (filtered["Zip Code"] == self.zipcode)
        ]

        if filtered.empty:
            raise MissingPersonError(
                f"The person '{self.name}' was not found in the dataframe"
            )

        df.drop(index=filtered.index, inplace=True)
        print(f"The person '{self.name}' was successfully deleted from the dataframe")

    @classmethod
    def get_stats(
        cls,
        df: pd.DataFrame,
        year: list[int] = None,
        gender: str | list = None,
        zipcode: str | list = None,
    ):
        """Class method to print the stats from a movies dataframe.

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with movies information.
        year : list[int], Default None
             List with two years range to filter.
        gender : str | list, Default None
            Gender or list of genders to filter.
        zipcode : int | list, Default None
            Zipcode or list of zipcodes to filter.
        """
        filtered = cls._filter(df, year=year, gender=gender, zipcode=zipcode)

        if not filtered.empty:

            oldest = filtered.loc[filtered["year of birth"].idxmin()]
            cls._print_stats(oldest, "Oldest Person")

            newest = filtered.loc[filtered["year of birth"].idxmax()]
            cls._print_stats(newest, "Youngest Person")
            cls._plot_stats(filtered)

        else:
            print("There are no movies that match does years and gender or zipcodes")

    @staticmethod
    def _plot_stats(df: pd.DataFrame) -> None:
        """Helper method to plot people dataframe stats

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the people information to be plotted.
        """
        sns.set_style("ticks")
        fig, axes = plt.subplot_mosaic(
            [["Year", "Year"], ["Zipcode", "Zipcode"]], figsize=(12, 8)
        )

        zipcode_df = pd.DataFrame(df.groupby("Zip Code").id.count()).reset_index()
        year_df = pd.DataFrame(df.groupby("year of birth").id.count()).reset_index()
        year_labels = year_df["year of birth"].to_list()
        zipcode_labels = zipcode_df["Zip Code"].to_list()
        sns.barplot(
            data=year_df,
            x="year of birth",
            y="id",
            hue="id",
            palette="Greens_d",
            legend=False,
            ax=axes["Year"],
        )
        sns.barplot(
            data=zipcode_df,
            x="Zip Code",
            y="id",
            hue="id",
            palette="Greens_d",
            legend=False,
            ax=axes["Zipcode"],
        )
        axes["Year"].set_ylabel("Frequency")
        axes["Year"].set_xlabel("Year")
        axes["Year"].set_xticks(range(len(year_labels)))  # Set the ticks
        axes["Year"].set_xticklabels(year_labels, rotation=45, ha="right")
        axes["Zipcode"].set_ylabel("Frequency")
        axes["Zipcode"].set_xlabel("Zipcode")
        axes["Zipcode"].set_xticks(range(len(zipcode_labels)))  # Set the ticks
        axes["Zipcode"].set_xticklabels(zipcode_labels, rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

    @classmethod
    def _check_structure(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Class method to validate the structure of a given people dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with people information.

        Returns
        -------
        pd.DataFrame
            Pandas dataframe formatted and validated.

        Raises
        ------
        MissingColumnsError
            If the validation fails.
        """
        expected_columns = ["id", "Full Name", "year of birth", "Zip Code", "Gender"]
        if set(expected_columns).issubset(df.columns):
            df.dropna(subset=expected_columns, inplace=True)
            return df

        raise MissingColumnsError(
            f"One or more columns are missing from the given dataframe. Expected columns are: {expected_columns}"
        )

    @staticmethod
    def _print_stats(df: pd.Series, title: str) -> None:
        """Helper function to print the stats

        Parameters
        ----------
        df : pd.Series
            Pandas series with the movies information
        title : str
            Title of the stats to print.

        Returns
        -------

        """
        bold = "\033[1m"
        end = "\033[0m"
        print(
            f"""
               {bold}{title}{end}: \n
                {bold}- Full Name:{end} {df['Full Name']} \n
                {bold}- Year of Birth:{end} {df['year of birth']} \n
                {bold}- Gender:{end} {df['Gender']} \n
                {bold}- Zipcode:{end} {df['Zip Code']} \n
               """
        )

    @staticmethod
    def _filter(
        df: pd.DataFrame,
        idx: int | list = None,
        name: str | list = None,
        year: list[int] = None,
        gender: str | list = None,
        zipcode: str | list = None,
    ) -> pd.DataFrame:
        """Helper function to filter a dataframe

        Parameters
        ----------
        df : pd.DataFrame
            Pandas dataframe with the people information.
        idx : int | list, Default None
            Index or list of index to filter.
        name : str | list, Default None
            Movie name or list of names to filter.
        year : list[int], Default None
            List with two years range to filter.
        gender : str, Default None
            Gender to filter by.
        zipcode : str | list, Default None
            Zipcode or list of zipcodes to filter.

        Returns
        -------
        pd.DataFrame
            Filtered pandas dataframe.
        """
        filtered = df.copy()
        if name:
            name = [name] if isinstance(name, str) else name
            filtered = filtered[filtered["Full Name"].isin(name)]

        if year:
            filtered = filtered[
                (filtered["year of birth"] >= min(year))
                & (filtered["year of birth"] <= max(year))
            ]

        if gender:
            filtered = filtered[filtered["Gender"] == gender]

        if zipcode:
            zipcode = [zipcode] if isinstance(zipcode, str) else zipcode
            zipcode = [str(z) for z in zipcode]
            filtered = filtered[filtered["Zip Code"].isin(zipcode)]

        if idx:
            idx = [idx] if isinstance(idx, int) else idx
            filtered = filtered[filtered["id"].isin(idx)]

        return filtered