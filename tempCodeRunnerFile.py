@app.route('/inventory')
def inventory():
    return render_template('inventory.html')