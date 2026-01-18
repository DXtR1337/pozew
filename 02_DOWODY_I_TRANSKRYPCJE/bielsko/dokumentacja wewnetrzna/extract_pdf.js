```javascript
const fs = require('fs');
const path = require('path');
const pdf = require('pdf-parse');

const baseDir = 'c:\\Users\\micha\\.gemini\\antigravity\\PROJEKT POZEW\\dokumentacja wewnetrzna';
const outputDir = 'c:\\Users\\micha\\.gemini\\antigravity\\PROJEKT POZEW\\dokumentacja wewnetrzna\\extracted_text';

if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

function getAllPdfFiles(dir, fileList = []) {
    const files = fs.readdirSync(dir);
    
    files.forEach(file => {
        const filePath = path.join(dir, file);
        if (fs.statSync(filePath).isDirectory()) {
            if (file !== 'extracted_text' && file !== 'node_modules') {
                getAllPdfFiles(filePath, fileList);
            }
        } else {
            if (path.extname(file).toLowerCase() === '.pdf') {
                fileList.push(filePath);
            }
        }
    });
    
    return fileList;
}

async function extractAll() {
    const allPdfs = getAllPdfFiles(baseDir);
    console.log(`Found ${ allPdfs.length } PDF files.`);

    for (const inputPath of allPdfs) {
        const fileName = path.basename(inputPath);
        // Create a unique output name to avoid collisions if files have same name in different folders
        // or just use valid filename characters
        const cleanName = fileName.replace(/[^a-z0-9\.]/gi, '_'); 
        const outputPath = path.join(outputDir, cleanName.replace('.pdf', '.txt'));

        console.log(`Extracting: ${ fileName }...`);
        try {
            const dataBuffer = fs.readFileSync(inputPath);
            const data = await pdf(dataBuffer);
            
            fs.writeFileSync(outputPath, data.text, 'utf8');
            console.log(`OK - ${ data.text.length } chars`);
        } catch (err) {
            console.error(`ERROR: ${ fileName } - ${ err.message } `);
        }
    }
    console.log('Done extraction.');
}

extractAll();
```
