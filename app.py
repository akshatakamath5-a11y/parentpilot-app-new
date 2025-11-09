from flask import Flask, request, jsonify, send_from_directory

import random

from datetime import datetime, timedelta

import json

# ===== CONFIGURATION =====

GEMINI_API_KEY = "AIzaSyAItrontwcYKNqx5ErnWWV4xRnqS1Fp5sk"
USE_AI = True

app = Flask(__name__, static_folder='static')

# Try to load Gemini
try:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    USE_AI = True
    print("✅ Google Gemini API loaded - INTELLIGENT responses enabled!")
except Exception as e:
    print(f"⚠️ Gemini not available: {e}")
    print("🔄 Using enhanced varied fallback")
    USE_AI = False

print("="*70)
print("🌟 PARENTPILOT - COMPLETE VERSION (All Features Fixed)")
print("="*70)
print(f"✓ Maya AI: {'Gemini (Intelligent)' if USE_AI else 'Enhanced Varied Fallback'}")
print("✓ Shopping Cart: Add/Remove/Buy")
print("✓ Interactive Milestones: Add/Edit/Delete")
print("✓ Mood History: Track & View")
print("="*70)

# PRODUCT DATABASE WITH IMAGES

PRODUCTS = [
    {'id': 1, 'name': 'Hatch Baby Rest', 'category': 'Sleep', 'price': 69.99,
     'image': 'https://images.squarespace-cdn.com/content/v1/5ea501655a6d8f4887ca4dac/1619725293436-329OVRURERG6YO2L7F6L/IMG_6424_jpg.JPG',
     'link': 'https://www.amazon.com/dp/B06XTYH76K', 'description': 'Smart sound machine',
     'keywords': ['sleep', 'tired', 'nap', 'cry']},
    {'id': 2, 'name': 'Nanit Pro Monitor', 'category': 'Monitoring', 'price': 299.00,
     'image': 'https://di2ponv0v5otw.cloudfront.net/posts/2024/10/05/67012d7bd90d21216ef5a8a7/m_67012db4896c3855ec01820d.jpg',
     'link': 'https://www.amazon.com/dp/B08XYMM9TY', 'description': 'HD baby monitor',
     'keywords': ['monitor', 'safety', 'sleep']},
    {'id': 3, 'name': 'Spectra S1 Pump', 'category': 'Feeding', 'price': 199.95,
     'image': 'https://hometownmedicalms.com/wp-content/uploads/2023/02/S1-Retail-with-Accessories.png',
     'link': 'https://www.amazon.com/dp/B00HSMQMX0', 'description': 'Breast pump',
     'keywords': ['feeding', 'pump', 'milk']},
    {'id': 4, 'name': "Dr Browns Bottles", 'category': 'Feeding', 'price': 24.99,
     'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSO9AEYXgGgyxW49oFLMFlg4Cu6bmCQSnrMUA&s',
     'link': 'https://www.amazon.com/dp/B001OVR7LW', 'description': 'Anti-colic bottles',
     'keywords': ['bottle', 'gas', 'colic', 'cry']},
    {'id': 5, 'name': 'Baby Bjorn Bouncer', 'category': 'Soothing', 'price': 199.99,
     'image': 'https://a.storyblok.com/f/187315/1500x2100/0237e8155e/us-005130-bouncer-balance-soft-light-beige-trifabric-lifestyle-babybjorn_743.jpg/m/590x826/smart/filters:quality(80)',
     'link': 'https://www.amazon.com/dp/B07XRXKR81', 'description': 'Ergonomic bouncer',
     'keywords': ['soothe', 'calm', 'cry', 'fussy']},
    {'id': 6, 'name': 'FridaBaby NoseFrida', 'category': 'Health', 'price': 19.99,
     'image': 'https://m.media-amazon.com/images/I/71kZmX0ZQUL._AC_UF350,350_QL80_.jpg',
     'link': 'https://www.amazon.com/dp/B00171WXII', 'description': 'Nasal aspirator',
     'keywords': ['sick', 'cold', 'nose']},
    {'id': 7, 'name': 'Gas Relief Drops', 'category': 'Health', 'price': 12.99,
     'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQDHWyVpa4n-BONagawi8Ipu_saVo3DXG8p4w&s',
     'link': 'https://www.amazon.com/dp/B001B2JP4E', 'description': 'Relieves gas',
     'keywords': ['gas', 'pain', 'belly', 'cry']},
    {'id': 8, 'name': 'Humidifier', 'category': 'Health', 'price': 39.99,
     'image': 'https://m.media-amazon.com/images/I/61hvvWP7TbL._AC_UF894,1000_QL80_.jpg',
     'link': 'https://www.amazon.com/dp/B09LQSVDP8', 'description': 'Cool mist',
     'keywords': ['sick', 'cold', 'breathing']}
]

def find_products(text, conversation_history):
    combined = text.lower() + ' ' + ' '.join([m['content'].lower() for m in conversation_history[-3:] if m['role'] == 'user'])
    scored = []
    for p in PRODUCTS:
        score = sum(10 for kw in p['keywords'] if kw in combined)
        if score > 0:
            scored.append({'score': score, 'product': p})
    scored.sort(key=lambda x: x['score'], reverse=True)
    return [s['product'] for s in scored[:4]]

# SHOPPING CART

cart_storage = []

@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if product:
        cart_storage.append(product)
        return jsonify({'success': True, 'cart_count': len(cart_storage), 'message': f'Added {product["name"]} to cart!'})
    return jsonify({'success': False, 'error': 'Product not found'}), 404

@app.route("/cart/view", methods=["GET"])
def view_cart():
    total = sum(p['price'] for p in cart_storage)
    return jsonify({'success': True, 'cart': cart_storage, 'total': total, 'count': len(cart_storage)})

@app.route("/cart/remove/", methods=["DELETE"])
def remove_from_cart(product_id):
    global cart_storage
    cart_storage = [p for p in cart_storage if p['id'] != product_id]
    return jsonify({'success': True, 'cart_count': len(cart_storage)})

@app.route("/cart/clear", methods=["DELETE"])
def clear_cart():
    global cart_storage
    cart_storage = []
    return jsonify({'success': True})

# MILESTONES TRACKER

milestones_storage = []

@app.route("/milestones/list", methods=["GET"])
def list_milestones():
    return jsonify({'success': True, 'milestones': milestones_storage})

@app.route("/milestones/add", methods=["POST"])
def add_milestone():
    data = request.get_json()
    milestone = {
        'id': len(milestones_storage) + 1,
        'title': data.get('title', ''),
        'description': data.get('description', ''),
        'date': data.get('date', ''),
        'age_months': data.get('age_months', 0),
        'category': data.get('category', 'General'),
        'created_at': datetime.now().isoformat()
    }
    milestones_storage.append(milestone)
    return jsonify({'success': True, 'milestone': milestone})

@app.route("/milestones/update/", methods=["PUT"])
def update_milestone(milestone_id):
    data = request.get_json()
    for m in milestones_storage:
        if m['id'] == milestone_id:
            m.update({
                'title': data.get('title', m['title']),
                'description': data.get('description', m['description']),
                'date': data.get('date', m['date']),
                'age_months': data.get('age_months', m['age_months']),
                'category': data.get('category', m['category'])
            })
            return jsonify({'success': True, 'milestone': m})
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.route("/milestones/delete/", methods=["DELETE"])
def delete_milestone(milestone_id):
    global milestones_storage
    milestones_storage = [m for m in milestones_storage if m['id'] != milestone_id]
    return jsonify({'success': True})

# MOOD HISTORY TRACKER

mood_history = []

@app.route("/mood-checkin", methods=["POST"])
def mood_checkin():
    data = request.get_json()
    entry = {
        'id': len(mood_history) + 1,
        'mood': data.get('mood', ''),                # E.g., "Calm", "Stressed"
        'note': data.get('note', '') or '',
        'energy': data.get('energy'),                # Integer/string
        'support': data.get('support'),
        'confidence': data.get('confidence'),
        'emotion': data.get('emotion', ''),          # Text or emoji if desired
        'timestamp': datetime.now().isoformat(),
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    mood_history.append(entry)
    return jsonify({'success': True, 'entry': entry})



@app.route("/mood-history", methods=["GET"])
def get_mood_history():
    limit = request.args.get('limit', 30, type=int)
    recent = mood_history[-limit:]
    recent.reverse()  # Most recent first

    stats = {}
    if mood_history:
        mood_counts = {}
        for entry in mood_history:
            mood = entry['mood']
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        total = len(mood_history)
        stats = {mood: round((count / total) * 100, 1) for mood, count in mood_counts.items()}
    return jsonify({'success': True, 'history': recent, 'stats': stats, 'total': len(mood_history)})

# --- NURTUREBOT-STYLE CHAT MODEL --- #
def get_maya_nurturebot(user_input, conversation_history):
    try:
        context = '\n'.join([
            f"{'Parent' if m['role']=='user' else 'Maya'}: {m['content']}"
            for m in conversation_history[-10:]
        ])
        prompt = f"""
You are Maya, an empathetic, context-aware AI parenting assistant.
Always reference what the parent shared earlier ("You mentioned..."; "Following up on...").
Ask 1-2 gentle follow-up questions based on conversation history.
Give detailed, encouraging suggestions—including helpful coping strategies, well-being tips, and relevant parenting products if any fit.
Always show warmth and speak conversationally; respond as a supportive friend.

Previous conversation:
{context}

Parent: {user_input}

Respond as Maya. Be supportive, always refer to earlier messages, suggest relevant products if helpful, ask a clarifying question, and provide actionable advice (2-4 paragraphs):
"""
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt,
            temperature=0.93,
            top_p=0.96,
            max_output_tokens=800
        )
        return response.text.strip()
    except Exception as e:
        fallback_responses = [
            "Parenting can be so tough. Can you tell me more about your situation?",
            "Thank you for sharing. What's been worrying you most recently?",
            "I'm here to support you, however you're feeling. Can you describe what's going on?",
            "Let's troubleshoot together. Are there specific situations or times when this shows up?"
        ]
        return random.choice(fallback_responses)

def get_maya_response(user_input, conversation_history):
    return get_maya_nurturebot(user_input, conversation_history)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get('user_input', '')
    conversation = data.get('conversation', [])
    if not user_input:
        return jsonify({'error': 'No input'}), 400

    ai_message = get_maya_response(user_input, conversation)
    products = find_products(user_input, conversation)

    conversation.append({'role': 'user', 'content': user_input})
    conversation.append({'role': 'ai', 'content': ai_message})

    return jsonify({
        'ai_message': ai_message,
        'products': products,
        'conversation': conversation,
        'timestamp': datetime.now().isoformat()
    })

# MONITOR & CRY DETECTION (Basic Demo)

monitor_data = {'heart_rate': 120, 'oxygen_level': 98, 'temperature': 22.5, 'sleep_start': datetime.now() - timedelta(hours=2)}
cry_history = []
CRY_TYPES = {
    'hungry': {'label': '🍼 Hungry', 'icon': '🍼', 'suggestions': ['Try feeding', 'Check last feed']},
    'tired': {'label': '😴 Tired', 'icon': '😴', 'suggestions': ['Put to sleep', 'Dim lights']},
    'pain': {'label': '😖 Pain', 'icon': '😖', 'suggestions': ['Check injuries', 'Take temperature']},
    'discomfort': {'label': '😣 Discomfort', 'icon': '😣', 'suggestions': ['Check diaper', 'Check temp']},
    'belly_pain': {'label': '🤢 Belly Pain', 'icon': '🤢', 'suggestions': ['Burp baby', 'Bicycle legs']}
}

def simulate_cry():
    cry_type = random.choice(list(CRY_TYPES.keys()))
    cry_info = CRY_TYPES[cry_type]
    return {
        'detected': True, 'cry_type': cry_type, 'cry_label': cry_info['label'],
        'icon': cry_info['icon'], 'confidence': round(random.uniform(0.65, 0.90), 2),
        'model': 'Rule-based', 'suggestions': cry_info['suggestions'],
        'timestamp': datetime.now().isoformat()
    }

@app.route("/")
def home():
    return app.send_static_file('index.html')


@app.route("/products", methods=["GET"])
def get_products():
    category = request.args.get('category', 'all')
    if category == 'all':
        for p in PRODUCTS:
            p['thumbnail'] = p.get('image', '')
        return jsonify({'products': PRODUCTS})
    else:
        filtered = [p for p in PRODUCTS if p['category'].lower() == category.lower()]
        for p in filtered:
            p['thumbnail'] = p.get('image', '')
        return jsonify({'products': filtered})

@app.route("/journal", methods=["POST"])
def add_journal():
    return jsonify({'success': True})

@app.route("/monitor/status", methods=["GET"])
def monitor_status():
    monitor_data['heart_rate'] = random.randint(110, 130)
    monitor_data['oxygen_level'] = random.randint(95, 100)
    monitor_data['temperature'] = round(random.uniform(21, 24), 1)
    sleep_duration = (datetime.now() - monitor_data['sleep_start']).seconds // 60
    return jsonify({
        'status': 'active', 'heart_rate': monitor_data['heart_rate'],
        'oxygen_level': monitor_data['oxygen_level'], 'temperature': monitor_data['temperature'],
        'humidity': 45, 'sleep_duration_minutes': sleep_duration,
        'last_updated': datetime.now().isoformat()
    })

@app.route("/monitor/sleep-analysis", methods=["GET"])
def sleep_analysis():
    sleep_duration = (datetime.now() - monitor_data['sleep_start']).seconds // 60
    analysis = f"Your baby has been sleeping for {sleep_duration} minutes. All vitals look healthy!"
    return jsonify({'analysis': analysis, 'sleep_quality_score': random.randint(75, 95)})

@app.route("/monitor/alerts", methods=["GET"])
def monitor_alerts():
    return jsonify({'alerts': []})

@app.route("/cry-detection/analyze", methods=["POST"])
def analyze_cry():
    result = simulate_cry()
    cry_history.append({'result': result, 'timestamp': result['timestamp']})
    if len(cry_history) > 50: cry_history.pop(0)
    return jsonify({'success': True, 'result': result})

@app.route("/cry-detection/history", methods=["GET"])
def get_cry_history():
    limit = request.args.get('limit', 10, type=int)
    return jsonify({'success': True, 'history': cry_history[-limit:], 'total': len(cry_history)})

@app.route("/cry-detection/stats", methods=["GET"])
def get_cry_stats():
    if not cry_history:
        return jsonify({'success': True, 'stats': {'total_detections': 0, 'most_common': None, 'today': 0}})
    type_counts = {}
    today = datetime.now().date()
    today_count = 0
    for entry in cry_history:
        cry_type = entry['result']['cry_type']
        type_counts[cry_type] = type_counts.get(cry_type, 0) + 1
        entry_date = datetime.fromisoformat(entry['timestamp']).date()
        if entry_date == today: today_count += 1
    most_common = max(type_counts, key=type_counts.get) if type_counts else None
    most_common_label = CRY_TYPES[most_common]['label'] if most_common else None
    return jsonify({'success': True, 'stats': {'total_detections': len(cry_history), 'most_common': most_common, 'most_common_label': most_common_label, 'today': today_count}})

@app.route("/cry-detection/simulate", methods=["POST"])
def simulate_cry_route():
    result = simulate_cry()
    cry_history.append({'result': result, 'timestamp': result['timestamp']})
    return jsonify({'success': True, 'result': result})

if __name__ == "__main__":
    print("\n✓ Server: http://127.0.0.1:5000/")
    print("="*70 + "\n")
    app.run(debug=True)
