# App Configuration Explanation (The Rule Book 📖)

Ee file mana application ki oka **Rule Book** laantidhi. Application motham ela pani cheyali, limits emiti, files ekkada daachali ane rules anni ikkade untayi.

### Line-by-Line Explanation:

- **Line 4 (MAX_FILE_SIZE = 2MB):**
  - **Endhuku 2MB?**: User 10MB or 20MB images upload chesthe server slow ayipothundhi, storage thondaraga nindipothundhi. Kabatti 2MB limit pettam.
  - **Inka em ivvachhu?**: Nuvvu kavali ante dhanni 5MB (`5 * 1024 * 1024`) or 1MB ki marchukovatam nee ishtam.

- **Line 5 (TARGET_MIN_BYTES = 15KB):**
  - **Endhuku 15KB?**: Image maree chinnaga (like 1KB or 2KB) unte clarity motham poyi, pixels kanipisthayi. Minimum 15KB unte clarity maintain avthundhi.

- **Line 6 (TARGET_MAX_BYTES = 295KB):**
  - **Endhuku 295KB?**: Normal ga websitelo images 300KB lopala unte page fast ga load avthundhi. User ki "Wait" chese thappu thagguthundhi.
  - **Inka em ivvachhu?**: Neeku high clarity images kaavali ante dhanni 500KB or 1MB kuda pettukovachhu.

- **Line 7-8 (QUALITY_FLOOR = 45, QUALITY_MAX = 95):**
  - **Endhuku ee range?**: 45 kante thaggithe image chudadaniki bagundadhu. 95 kante ekkuva unte file size vipareetham ga peruguthundhi kani clarity lo peddha difference undadhu.

- **Line 10-16 (Allowed Formats):**
  - Ikkada `.jpg, .png, .webp` lanti common formats matrame allow chesthunnam. Endhukante ivi fast ga load avthayi. `.tiff` or `.bmp` lanti heavy files ni allow cheyatledhu.

- **Line 18-20 (Storage Paths):**
  - Images ekkada save avvali (`storage` folder) and reports (logs) ekkada undali (`logs` folder) ani computer ki path chupisthunnam.

- **Line 22-23 (Media URL):**
  - Image save ayyaka browser lo open cheyadaniki `http://localhost:5000/media/...` ane link format create chesthunnam.
  - **Inka em ivvachhu?**: Live server ki poyinappudu `localhost` badulu nee domain name (eg: `https://mywebsite.com`) ivvachhu.

- **Line 25-30 (Logging):**
  - Application lo em jaruguthundho (Status: ADDED, REPLACED, DELETED) oka file lo record chesthunnam. Dhanni `app.log` antaru.

- **Line 33-45 (Functions):**
  - `init_directories`: Modhalu pettagaane folders levu ante create chesthadhi.
  - `website_folder`: Prathi website ki oka separate folder (compartment) create chesthadhi. Image mix-up avvakunda chusthadhi.

### Endhuku ee values ichhau?
Ee values anni **"Web Best Practices"** base cheskuni ichhanu. Ante, oka website smooth ga, fast ga work avvalante images ela undalo ala set chesanu. 

**Tips for you:**
1. Website chala fast ga load avvali ante: `TARGET_MAX_BYTES` ni thagginchu (eg: 150KB).
2. Images chala HD ga kanipinchali ante: `QUALITY_FLOOR` ni penchu (eg: 70) and `TARGET_MAX_BYTES` ni penchu (eg: 800KB).

**Summary:** Rule book lo rules correct ga unte, application discipline ga pani chesthadhi mowa!
