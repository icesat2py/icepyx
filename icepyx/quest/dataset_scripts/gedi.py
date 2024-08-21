from icepyx.quest.dataset_scripts.dataset import DataSet

class Gedi(DataSet):

	def __init__(self):
		pass

	def search_data(self):
		"""
		Query the dataset (i.e. search for available data)
		given the spatiotemporal criteria and other parameters specific to the dataset.
		"""
		raise NotImplementedError

	def download(self):
		"""
		Download the data to your local machine.
		"""
		raise NotImplementedError

	def save(self, filepath):
		"""
		Save the downloaded data to a directory on your local machine.
		"""
		raise NotImplementedError