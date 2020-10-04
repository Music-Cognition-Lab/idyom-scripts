'''
Utility to export IDyOM database (most likely sqlite) as a Pandas DataFrame.

Tom Kaplan
'''
import pandas as pd

# Default IDyOM database name
DB_PATH = 'database.sqlite'

class IDyOMDatabase(object):

    def __init__(self, path):
        self._path = path
        self.composition_df = None
        self.dataset_df = None
        self.event_df = None
        self.all_df = None

    @classmethod
    def from_sqlite(cls, path):
        obj = cls(path)
        obj.load_sqlite()
        return obj.all_df

    def load_sqlite(self):
        from sqlite3 import connect

        # Load the three IDyOM tables
        with connect(self._path) as conn:
            self.composition_df = pd.read_sql_query("SELECT * FROM MTP_COMPOSITION;", conn)
            self.dataset_df = pd.read_sql_query("SELECT * FROM MTP_DATASET;", conn)
            self.event_df = pd.read_sql_query("SELECT * FROM MTP_EVENT;", conn)

        # Merge tables, as far as possible
        self._merge_dfs()

    def _merge_dfs(self):
        non_empty = lambda df: df is not None and not df.empty

        # First, see if a dataset/composition index is possible
        if non_empty(self.dataset_df) and non_empty(self.composition_df):
            self.all_df = pd.merge(self.dataset_df, self.composition_df, how='outer',
                                   on='DATASET_ID', suffixes=('_DATASET', '_COMPOSITION'))

            # Second, see if events can be joined onto the dataset/composition index
            if non_empty(self.event_df):
                self.all_df = pd.merge(self.all_df, self.event_df, how='outer',
                                       on=['DATASET_ID', 'COMPOSITION_ID'])

