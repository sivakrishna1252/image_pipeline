# Gallery Service Explanation (The Manager 👨‍💼)

Ee file mana motham operation ni manage chesthundhi. Idhi coordinator laanti dhi. 

### Line-by-Line Explanation:

- **Line 15-32 (Downloader):** 
  - Oka vela user image pampaka poyina, direct URL isthe internet nundi image ni download chesthadhi.

- **Line 37 (`upload_image`):** 
  - Idhi main manager office table. Ekkade control start avthundhi.

- **Line 58 & 63 (Verification):** 
  - Manager ventane **ImageValidator (Guard)** ni pilichi "Pampina image correct aa kaadha check cheyi" ani cheptadu.

- **Line 71-78 (Registry):** 
  - Aa website ki already enni images unnayo list teeskuni memory lo pettukuntadhi.

- **Line 82-93 (Replacement Logic):** 
  - Oka vela manam "Patha file ni teesi kothadhi pettu" ante, patha file ni search chesi delete chesi, kothadhanni process chesthadhi.

- **Line 96 (The Call to Engine):** 
  - Ikkade `compress_to_webp` (Pipeline Engine) ni manager request chesthadhi. "Size thagginchi kotha format lo ivvu" ani.

- **Line 101-102 (Unique ID):** 
  - `timestamp_ms = int(time.time() * 1000)`: Prathi image ki website name + current time thoti oka unique ID generate chesthadhi. 
  - Dhinivalla okka website ki 100 images unna, okadha peru inkodhaniki matching avvadhu.

- **Line 114 (Public URL):** 
  - Image save ayyaka, browser lo chusukodaniki kaavalsina Link (URL) ni create chesthadhi.

- **Line 135-170 (Get Gallery):** 
  - User "Ma website images anni chupinchu" ani adugithe, registry check chesi list isthadhi.

- **Line 182-235 (Deletion):** 
  - Avatharam tharavatha image waste anukunte, dhanni permanent ga delete chesi clear chesthadhi.

**Summary:** Manager anni departments (Guard, Engine, Storage) ni coordinate chesthu, mana image process ni smooth ga jarigetattu chesthadu.
