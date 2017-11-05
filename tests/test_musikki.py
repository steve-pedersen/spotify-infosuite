from musikki.musikki import search, Artist
import json
import unittest


class TestArtist(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.artist = search('Mogwai', 'Coolverine', "Every Country's Sun")

	def test_artist(self):
		self.assertIsInstance(self.artist, Artist)

	def test_artist_album(self):
		self.assertEqual(self.artist.album(), "Every Country's Sun")

	def test_reviev_artist(self):
		self.assertEqual(self.artist.artist(), 'Mogwai')

	def test_artist_label(self):
		self.assertEqual(self.artist.label(), 'Chemikal Underground')

	def test_artist_year(self):
		self.assertEqual(self.artist.year(), '1999/2014')

	def test_score(self):
		self.assertEqual(self.artist.score(), 8.3)

	def test_editorial(self):
		self.assertTrue(self.artist.editorial().startswith('Though few of their songs contain actual words'))

	def test_artist_url(self):
		self.assertEqual(self.artist.url, '/reviews/albums/19466-mogwai-come-on-die-young-deluxe-edition/')

	def test_artist_to_json(self):
		input_dict = self.artist._json_safe_dict()
		output_dict = json.loads(self.artist.to_json())
		for input_key in input_dict.keys():
			self.assertEqual(output_dict[input_key], input_dict[input_key])

if __name__ == '__main__':
	unittest.main()