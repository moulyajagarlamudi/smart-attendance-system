const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from the file_zip directory
app.use(express.static(path.join(__dirname, 'file_zip')));

// Serve the main home.html file (portal landing page)
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'file_zip', 'home.html'));
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
    console.log(`Student Portal is accessible at http://localhost:${PORT}`);
}); 