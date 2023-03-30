"""
azure voice service
"""
import time
import azure.cognitiveservices.speech as speechsdk
from bridge.reply import Reply, ReplyType
from common.log import logger
from common.tmp_dir import TmpDir
from voice.voice import Voice
from config import conf

class AzureVoice(Voice):
    speech_config = speechsdk.SpeechConfig(subscription=conf().get('azure_speech_key'), region=conf().get('azure_service_region'))
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    speech_config.speech_synthesis_voice_name=conf().get('azure_voice_name')
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)    
    
    def __init__(self):
        pass

    def voiceToText(self, voice_file):
        pass

    def textToVoice(self, text):
        result = self.speech_synthesizer.speak_text_async(text).get()
        if not isinstance(result, dict):
            fileName = TmpDir().path() + 'voice_response_' + str(int(time.time())) + '.mp3'
            with open(fileName, 'wb') as f:
                f.write(result.audio_data)
            logger.info('[Azure] textToVoice text={} voice file name={}'.format(text, fileName))
            reply = Reply(ReplyType.VOICE, fileName)
        else:
            logger.error('[Azure] textToVoice error={}'.format(result))
            reply = Reply(ReplyType.ERROR, "抱歉，语音合成失败")
        return reply
