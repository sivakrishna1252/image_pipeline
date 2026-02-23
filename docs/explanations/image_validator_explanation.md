# Image Validator Explanation (Security Guard 💂‍♂️)

Ee file mana application ki oka **Security Guard** laantidhi. Image lopalki rakamundhe, adhi safe aa kaadha, rules follow avthundha ledha ani check chesthundhi.

### Line-by-Line Explanation:

- **Line 1-5 (Imports):** 
  - `logging`: Edo thappu jarigina, ledha em jaruguthundo record (log) cheyadaniki.
  - `BytesIO`: Image data ni memory lo thalkaya noppi lekunda handle cheyadaniki.
  - `PIL (Pillow)`: Image ni open chesi chudadaniki main tool.
  - `Config`: Mana rules (allowed formats, max size) anni ikkade untayi.

- **Line 8-10 (The Function):** 
  - `class ImageValidator`: Idhi oka module.
  - `def validate(file)`: Ee function ki image ni isthe, adhi "Correct" or "Wrong" ani chepthundhi.

- **Line 13-20 (Reading Data):** 
  - User pampina data ni computer ki ardham ayye `bytes` loki marchuthunnam. Computer ki image ante just numbers (bytes) matrame.

- **Line 22-31 (Format Check):** 
  - `ext = filename.rsplit(".", 1)[-1].lower()`: Image peru chivara emundho chusthadhi (eg: .jpg). 
  - Adhi `.jpg, .jpeg, .png, .webp, .gif` kaakunda inkemaina (like .exe or .pdf) unte, ventane reject chesthadhi.

- **Line 33-40 (Calculations):** 
  - `size_kb = size_bytes / 1024`: Bytes ni kilo-bytes loki marchadam.
  - Ikkada calculations endhuku ante, manaki size entha undo telusthene rule apply cheyagalam.

- **Line 42-48 (Size Rule):** 
  - `if size_bytes > Config.MAX_FILE_SIZE`: Oka vela image 2MB (mana rule) kante ekkuva unte, "Size ekkuva undhi" ani error isthadhi.

- **Line 50-60 (Integrity Check):** 
  - `img.verify()`: Image file nijamga image aa ledha fake aa (corrupt file) ani check chesthadhi.
  - `width, height = img.size`: Image entha podavu, entha వెడల్పు undo dimensions teeskuntadhi.

- **Line 66 (Success):** 
  - Anni correct ga unte, image data ni and dhani dimensions ni return chesthadhi. 

**Summary:** Guard image ni check chesi, bagunte lopalaki (processing ki) pampisthadu.
