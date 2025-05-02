# steve-jobs-elastic
## How to run?

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/steve-jobs-elastic.git
cd steve-jobs-elastic
```

### 2. Create a `.env` File

This file should contain your private API keys required for the services:

```env
# .env
ES_API_KEY=your_elasticsearch_key_here
OPENAI_API_KEY=your_openai_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

> 💡 You must create accounts with [Elastic Cloud](https://cloud.elastic.co/), [OpenAI](https://platform.openai.com/account/api-keys), and [ElevenLabs](https://www.elevenlabs.io/) to get these API keys.

### 3. Install Dependencies


```bash
pip install openai elasticsearch elevenlabs python-dotenv
```

### 4. Run the Application

```bash
python main.py
```

This will launch the application.
