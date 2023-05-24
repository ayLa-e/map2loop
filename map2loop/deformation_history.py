import pandas
import numpy
import beartype
import geopandas
import math


class DeformationHistory:
    """
    A class containing all the fault and fold summaries and relationships

    Attributes
    ----------
    minimum_fault_length_to_export: float
        The cutoff for ignoring faults. Any fault shorter than this is not exported
    history: list
        The time ordered list of deformation events
    faultColumns: numpy.dtype
        Column names and types for fault summary
    foldColumns: numpy.dtype
        Column names and types for fold summary
    faults: pandas.DataFrame
        The fault summary
    folds: pandas.DataFrame
        The fold summary

    """
    def __init__(self):
        """
        The initialiser for the deformation history. All attributes are defaulted
        """
        self.minimum_fault_length_to_export = 500.0
        self.history = []
        self.fault_fault_relationships = []

        # Create empty fault and fold dataframes
        self.faultColumns = numpy.dtype(
            [
                ("eventId", int),
                ("name", str),
                ("minAge", float),
                ("maxAge", float),
                ("group", str),
                ("avgDisplacement", float),
                ("avgDownthrowDir", float),
                ("influenceDirection", float),
                ("verticalRadius", float),
                ("horizontalRadius", float),
                ("colour", str),
                ("centreX", float),
                ("centreY", float),
                ("centreZ", float),
                ("avgSlipDirX", float),
                ("avgSlipDirY", float),
                ("avgSlipDirZ", float),
                ("avgNormalX", float),
                ("avgNormalY", float),
                ("avgNormalZ", float),
                ("length", float),
            ]
        )
        self.faults = pandas.DataFrame(numpy.empty(0, dtype=self.faultColumns))
        # self.faults = self.faults.set_index("name")

        self.foldColumns = numpy.dtype(
            [
                ("eventId", int),
                ("name", str),
                ("minAge", float),
                ("maxAge", float),
                ("periodic", bool),
                ("wavelength", float),
                ("amplitude", float),
                ("asymmetry", bool),
                ("asymmetryShift", float),
                ("secondaryWavelength", float),
                ("secondaryAmplitude", float),
            ]
        )
        self.folds = pandas.DataFrame(numpy.empty(0, dtype=self.foldColumns))
        # self.folds = self.folds.set_index("name")

    def set_minimum_fault_length(self, length):
        """
        Sets the minimum fault length to export

        Args:
            length (float or int):
                The fault length cutoff
        """
        self.minimum_fault_length_to_export = length

    def get_minimum_fault_length(self):
        """
        Getter for the fault length cutoff

        Returns:
            float: The fault length cutoff
        """
        return self.minimum_fault_length_to_export

    def findfault(self, id):
        """
        Find the fault in the summary based on its eventId

        Args:
            id (int or str):
                The eventId or name to look for

        Returns:
            pandas.DataFrame: The sliced data frame containing the requested fault
        """
        if type(id) == int:
            return self.faults[self.faults["eventId"] == id]
        elif type(id) == str:
            return self.faults[self.faults["name"] == id]
        else:
            print("ERROR: Unknown identifier type used to find fault")

    def findfold(self, id):
        """
        Find the fold in the summary based on its eventId

        Args:
            id (int or str):
                The eventId or name to look for

        Returns:
            pandas.DataFrame: The sliced data frame containing the requested fold
        """
        if type(id) == int:
            return self.folds[self.folds["foldId"] == id]
        elif type(id) == str:
            return self.folds[self.folds["name"] == id]
        else:
            print("ERROR: Unknown identifier type used to find fold")

    def addFault(self, fault):
        """
        Add fault to the fault summary

        Args:
            fault (pandas.DataFrame or dict):
                The fault information to add
        """
        if type(fault) == pandas.DataFrame or type(fault) == dict:
            if "name" in fault.keys():
                if fault["name"] in self.faults.index:
                    print("Replacing fault", fault["name"])
                self.faults[fault["name"]] = fault
            else:
                print("No name field in fault", fault)
        else:
            print("Cannot add fault to dataframe with type", type(fault))

    def removeFaultByName(self, name: str):
        """
        Remove the fault from the summary by name

        Args:
            name (str):
                The name of the fault(s) to remove
        """
        self.faults = self.faults[self.faults["name"] != name].copy()

    def removeFaultByEventId(self, eventId: int):
        """
        Remove the fault from the summary by eventId

        Args:
            eventId (int):
                The eventId of the fault to remove
        """
        self.faults = self.faults[self.faults["eventId"] != eventId].copy()

    def addFold(self, fold):
        """
        Add fold to the fold summary

        Args:
            fold (pandas.DataFrame or dict):
                The fold information to add
        """
        if type(fold) == pandas.DataFrame or type(fold) == dict:
            if "name" in fold.keys():
                if fold["name"] in self.folds.index:
                    print("Replacing fold", fold["name"])
                self.folds[fold["name"]] = fold
            else:
                print("No name field in fold", fold)
        else:
            print("Cannot add fold to dataframe with type", type(fold))

    @beartype.beartype
    def populate(self, faults_map_data: geopandas.GeoDataFrame):
        """
        Populate the fault (and fold) summaries from a geodataframe

        Args:
            faults_map_data (geopandas.GeoDataFrame):
                The parsed data frame from the map
        """
        if faults_map_data.shape[0] == 0:
            return
        faults_data = faults_map_data.copy()
        faults_data = faults_data.dissolve(by="NAME", as_index=False)
        faults_data = faults_data.reset_index(drop=True)

        self.stratigraphicUnits = pandas.DataFrame(
            numpy.empty(faults_data.shape[0], dtype=self.faultColumns)
        )
        self.faults["eventId"] = faults_data["ID"]
        self.faults["name"] = faults_data["NAME"]
        self.faults["minAge"] = -1
        self.faults["maxAge"] = -1
        self.faults["group"] = ""
        self.faults["supergroup"] = ""
        self.faults["avgDisplacement"] = 1
        self.faults["avgDownthrowDir"] = 0
        self.faults["influenceDistance"] = 0
        self.faults["verticalRadius"] = 0
        self.faults["horizontalRadius"] = 0
        self.faults["colour"] = "#000000"
        self.faults["centreX"] = 0
        self.faults["centreY"] = 0
        self.faults["centreZ"] = 0
        self.faults["avgSlipDirX"] = 0
        self.faults["avgSlipDirY"] = 0
        self.faults["avgSlipDirZ"] = 0
        self.faults["avgNormalX"] = 0
        self.faults["avgNormalY"] = 0
        self.faults["avgNormalZ"] = 0
        self.faults["length"] = faults_data.geometry.length
        for index, fault in self.faults.iterrows():
            bounds = faults_map_data[faults_map_data["ID"] == fault["eventId"]].geometry.bounds
            xdist = bounds.maxx - bounds.minx
            ydist = bounds.maxy - bounds.miny
            length = math.sqrt(xdist*xdist + ydist*ydist)
            self.faults.at[index, "verticalRadius"] = length
            self.faults.at[index, "horizontalRadius"] = length / 2.0
            self.faults.at[index, "influenceDistance"] = length / 4.0

    @beartype.beartype
    def summarise_data(self, fault_observations: pandas.DataFrame):
        """
        Use fault observations data to add summary data for each fault

        Args:
            fault_observations (pandas.DataFrame):
                The fault observations data
        """
        id_list = self.faults["eventId"].unique()
        for id in id_list:
            observations = fault_observations[fault_observations["ID"] == id]
            if len(observations) < 2:
                self.removeFaultByEventId(id)

        # id_list = self.faults["eventId"].unique()
        for index, fault in self.faults.iterrows():
            observations = fault_observations[fault_observations["ID"] == fault["eventId"]]
            # calculate centre point
            self.faults.at[index, "centreX"] = numpy.mean(observations["X"])
            self.faults.at[index, "centreY"] = numpy.mean(observations["Y"])
            self.faults.at[index, "centreZ"] = numpy.mean(observations["Z"])

    def get_faults_for_export(self):
        """
        Get the faults for export (removes any fault that is shorter than the cutoff)

        Returns:
            pandas.DataFrame: The filtered fault summary
        """
        return self.faults[self.faults["length"] >= self.minimum_fault_length_to_export].copy()