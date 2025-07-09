
# Pandas/NumPy Kompatibilitäts-Fixes
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Alternative zu Pandas DataFrame
class SimpleDataFrame:
    def __init__(self, data):
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            self.data = data
            self.columns = list(data[0].keys()) if data else []
        else:
            self.data = []
            self.columns = []
    
    def __getitem__(self, column):
        return [row.get(column, None) for row in self.data]
    
    def tolist(self):
        return self.data

# Komplett pandas-freie Implementierung
PANDAS_AVAILABLE = False

# Dummy-Pandas ohne echten Import
class DummyPandas:
    @staticmethod
    def DataFrame(data):
        return SimpleDataFrame(data)

class DummyNumpy:
    pass

# Setze Dummy-Objekte
pd = DummyPandas()
np = DummyNumpy()

print("🔧 Pandas/NumPy komplett deaktiviert - verwende reine Python-Implementierung")
