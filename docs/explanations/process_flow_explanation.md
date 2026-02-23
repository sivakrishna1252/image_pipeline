# Image Pipeline Process Flow (How it works?) 🚀

Ee motham system ela pani chesthundhi ane sequence ikkada undhi:

### 1. The Rules (Config) 📖
Software start avvagane `config.py` nundi rules telusukuntundhi. 
*   "2MB kante peddhaga undakudadhu" 
*   "JPG/PNG mathrame ravali"

### 2. The Entry (Gallery Service) 📥
User image upload chesina, or URL ichina... modhalu velledhi `gallery_service.py` daggiraki. Idhi Coordinator (Manager) laantidhi.

### 3. The Security Check (Validator) 💂‍♂️
Manager ventane `image_validator.py` కి పంపిస్తాడు. 
*   **Validator logic:** "Config rules prakaram image size okay na? Format okay na?" ani check chesthadhi.
*   Anni bagunte "Green Signal" isthadhi.

### 4. The Transformation (Pipeline) ⚙️
Check-up ayyaka, Manager `image_pipeline.py` కి పంపిస్తాడు.
*   **Pipeline logic:** Ikkada **Calculations** jaruguthayi. Peddha image ni chinnadhi cheyadam, resolution marchadam, WebP format loki change cheyadam motham ikkade.

### 5. Final Output (The Result) 🖼️
Pipeline pani finish ayyaka, Manager aa image ni teeskuni:
*   Specified folder లో save chesthadhi.
*   User కి "Idigo nee Image URL" ani response isthadhi.

---

### Sequence logic (Coder perspective):
1. **Initialize:** Config
2. **Handle Request:** GalleryService
3. **Validate:** ImageValidator (uses Config)
4. **Process:** ImagePipeline (resize/compress)
5. **Response:** GalleryService (save & return)

**Note:** Gallery Service anedhi 'Glue' laantidhi. Anni files ni kalipi unchuthundhi.
