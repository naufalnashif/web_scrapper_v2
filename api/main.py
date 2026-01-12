from flask import Flask, jsonify, request
from scrapers.instagram import InstagramScraper

app = Flask(__name__)

@app.route('/api/scrape', methods=['GET'])
def scrape():
    platform = request.args.get('platform')
    target = request.args.get('target')
    
    if platform == 'instagram':
        # Secara scalable, API memanggil class yang sama
        data = InstagramScraper().get_detailed_data(target)
        return jsonify(data)
    
    return jsonify({"error": "Unsupported platform"}), 400

if __name__ == '__main__':
    app.run(port=5000)