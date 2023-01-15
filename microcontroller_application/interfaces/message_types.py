from dataclasses import dataclass
from typing import Any

# Any is used as a placeholder for all the types we expect


# Interface 01.1
FromPreferencesToProxy = Any
# Interface 01.2
FromProxyToPreferences = Any

# Interface 02
FromAggregationToProxy = Any
# Interface 03
FromHumanDetectionToActivityRecognition = Any
# Interface 04
FromHumanDetectionToPersonIdentification = Any
# Interface 05
FromActivityRecognitionToControl = Any
# Interface 06
FromPersonIdentificationToControl = Any
# Interface 07
FromPreferencesToControl = Any
# Interface 08
FromProxyToPersonIdentification = Any
# Interface 09
FromPersonIdentificationToProxy = Any
# Interface 10
FromPersonIdentificationToAggregation = Any
# Interface 11
FromControlToAggregation = Any
# Interface 12
# Interface 13
FromEnvironmentToHumanDetection = Any
# Interface 14
FromEnvironmentToControl = Any
# Interface 15
FromEnvironmentToAggregation = Any
