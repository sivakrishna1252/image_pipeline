# Image Pipeline Explanation (The Engine/Kitchen ⚙️)

Idhi mana application ki hardhayam laantidhi. Ikkade image size thaggadam, quality adjust avvadam lanti **Calculations** motham jaruguthayi.

### Main Logic & Calculations:

- **Line 16-22 (Resolution Rules - calculations):** 
  - Image lo enni pixels unnayo calculate chesthunnam (`MP = width * height / 1,000,000`).
  - Ekkua pixels (eg: 8MP) unte, dhanni 1600px ki thaggistham. Idhi endhuku ante, website speed thaggakunda chudadaniki.

- **Line 26-32 (Size-Quality Map):** 
  - Idhi oka smart logic table. 
  - Image size 1.5MB - 2.0MB unte: Quality 55% ki thaggistham.
  - Image size 0 - 300KB unte: Quality 80% (high) unchutham.
  - Ante peddha images ni ekkuva thaggistham, chinna images quality ni padigodtham.

- **Line 57-70 (Resizing Logic):** 
  - Ikkada simple math vadutham: `new_h = int(h * max_dim / w)`.
  - Image height and width proportions (aspect ratio) marakunda size thaggistham. Ante image sagga-padadhu kani chinnadhi avthundhi.

- **Line 81 (`compress_to_webp` function):** 
  - Idhe main process start chese place.

- **Line 120-130 (The Compression Loop):** 
  - `while len(best_bytes) >= _TARGET_MAX`: 
  - Image inka 300KB (target) kante ekkuva unte, quality ni prathi saari 5% thaggisthu loop thipputham. 
  - Target size vache daka ee loop thiruguthune untundhi. Idhi oka repetitive calculation.

- **Line 133-145 (Quality Recovery):** 
  - Oka vela compression valla image chala chinnadhi (eg: 20KB) ayipothe, clarity miss avthundhi. 
  - Appudu light ga quality periginchi (recovery), target size limit lopale best clarity ichela chesthadhi.

- **Line 150-163 (Final Stats):** 
  - `reduction = ((original_kb - final_kb) / original_kb * 100)`: 
  - Final ga image size entha thaggindhi ani percentage calculate chesthadhi.

- **Line 171-181 (Saving):** 
  - Final ga image ni computer disk lo save chesthadhi.

**Summary:** Engine image ni teeskuni, dhaaniki math rules apply chesi, size thaggichi, super ga polish chesi ready chesthadhi.
