from typing import Union, Dict, List, Tuple, Optional
from allennlp.predictors.predictor import Predictor

import rootpath

rootpath.append()
from backend.classifiers.classifierbase import ClassifierBase
import configurations


class Event2MindClassifier(ClassifierBase):
    URL_EVENT2MIND = "https://s3-us-west-2.amazonaws.com/allennlp/models/event2mind-2018.10.26.tar.gz"
    X_INTENT = 0
    X_REACTION = 1
    Y_REACTION = 2
    INTENT_TOKENS = 'xintent_top_k_predicted_tokens'
    INTENT_PROB = 'xintent_top_k_log_probabilities'
    REACTION_X_TOKENS = 'xreact_top_k_predicted_tokens'
    REACTION_X_PROB = 'xreact_top_k_log_probabilities'
    REACTION_Y_TOKENS = 'oreact_top_k_predicted_tokens'
    REACTION_Y_PROB = 'oreact_top_k_log_probabilities'

    def set_model(self, model: Union[object, str] = None) -> None:
        # set up emotion predictor

        if model:
            self.model = Predictor.from_path(model)
        else:
            self.model = Predictor.from_path(configurations.EVENT2MIND_MODEL_PATH)

    def predict(self, text: str, target: Optional[int] = None) -> Union[Dict, List, Tuple]:
        predictions = self.model.predict(source=text)

        intent = predictions[Event2MindClassifier.INTENT_TOKENS]
        probabilities_intent = predictions[Event2MindClassifier.INTENT_PROB]

        reactions_x = predictions[Event2MindClassifier.REACTION_X_TOKENS]
        probabilities_x = predictions[Event2MindClassifier.REACTION_X_PROB]

        reactions_y = predictions[Event2MindClassifier.REACTION_Y_TOKENS]
        probabilities_y = predictions[Event2MindClassifier.REACTION_Y_PROB]
        dict_intent = {Event2MindClassifier.INTENT_TOKENS: intent,
                       Event2MindClassifier.INTENT_PROB: probabilities_intent}
        dict_x_reaction = {Event2MindClassifier.REACTION_X_TOKENS: reactions_x,
                           Event2MindClassifier.REACTION_X_PROB: probabilities_x}
        dict_y_reaction = {Event2MindClassifier.REACTION_Y_TOKENS: reactions_y,
                           Event2MindClassifier.REACTION_Y_PROB: probabilities_y}

        if target == Event2MindClassifier.X_INTENT:

            return dict_intent
        elif target == Event2MindClassifier.X_REACTION:

            return dict_x_reaction
        elif target == Event2MindClassifier.Y_REACTION:

            return dict_y_reaction
        else:
            dict_all = dict_intent.copy()
            dict_all.update(dict_x_reaction)
            dict_all.update(dict_y_reaction)

            return dict_all


if __name__ == '__main__':
    # set up an event2mind classifier
    event2mindClassifier = Event2MindClassifier()

    # if event2mind model already exists locally, no parameter to pass
    event2mindClassifier.set_model()

    # if event2mind model doesn't exist locally, get model from url
    event2mindClassifier.set_model(Event2MindClassifier.URL_EVENT2MIND)

    # predict a text like "hello", specify what to extract: X_INTENT or X_REACTION or Y_REACTION
    dict_intent = event2mindClassifier.predict("hello", event2mindClassifier.X_INTENT)
    print(dict_intent)

    # if not specified, output all the results including x's intents, x's reactions and y's reactions
    print(event2mindClassifier.predict("hello"))
