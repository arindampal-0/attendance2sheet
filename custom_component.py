"""custom components"""


from collections.abc import Callable
from typing import TypedDict

import streamlit
import streamlit.components.v2

@streamlit.cache_resource
def register_detection_visualizer():
    """register detection visualizer"""
    return streamlit.components.v2.component(
        "detection_visualizer",
        html="""
            <div class="dv-container">
                <img class="dv-image" />
                <div class="dv-bounding-box"></div>
                <div class="dv-detection-validation-container">
                    <input class="dv-roll-text-input" type="text" />
                    <button class="dv-accept-button">✅</button>
                    <button class="dv-reject-button">❌</button>
                </div>
                <div class="dv-index-navigation-container">
                    <button class="dv-index-prev">Prev</button>
                    <button class="dv-index-next">Next</button>
                </div>
            </div>
        """,
        css="""
            .dv-container {
                position: relative;
                // width: 100%;
                padding: 0px;
            }

            .dv-container:focus {
                outline: 2px solid blue;
            }

            .dv-image {
                width: 100%;
            }

            .dv-bounding-box {
                position: absolute;
                left: 0;
                top: 0;
                width: 200px;
                height: 20px;
                background-color: transparent;
                border: 3px solid red;
                border-radius: 4px;
            }

            .dv-detection-validation-container {
                position: absolute;
                left: 0;
                top: 0;
                width: fit-content;
                display: flex;
                flex-direction: row;
                justify-content: center;
                align-items: center;
                gap: 4px;
                padding: 4px;
                background-color: rgba(255, 255, 255, .6);
                border-radius: 4px;

                .dv-roll-text-input {
                    width: 160px;
                    color: white;
                    font-size: 24px;
                }

                button {
                    padding: 0;
                    font-size: 24px;
                }
            }

            .dv-index-navigation-container {
                position: absolute;
                left: 0;
                top: 0;
                width: fit-content;
                display: flex;
                flex-direction: row;
                justify-content: center;
                align-items: center;
                gap: 4px;
                padding: 4px;
                background-color: rgba(255, 255, 255, .6);
                border-radius: 4px;

                button {
                    font-size: 20px;
                }
            }
        """,
        js="""
            export default function(component) {
                const {parentElement, data} = component;

                // survives hot reload, because it lives on the element
                let ctx = parentElement.__ctx;

                // kills listeners from any previous module instance
                ctx?.ac?.abort();

                if (!ctx) {
                    const root = parentElement.querySelector(".dv-container");
                    ctx = parentElement.__ctx = {root};
                }
                
                ctx.ac = new AbortController();

                // FIXME: this not working
                function handleKeyupEvent(event) {
                    console.log("handleKeyupEvent");
                    console.log(document.activeElement);
                    console.log(ctx.root);
                    
                    if (document.activeElement !== ctx.root) {
                        return;
                    }

                    if (event.key === "ArrowLeft") {
                        ctx.args.setTriggerValue("index_step", -1);
                    } else if (event.key === "ArrowRight") {
                        ctx.args.setTriggerValue("index_step", 1);
                    }
                }
                // ctx.root.addEventListener("keyup", handleKeyupEvent, {signal: ctx.ac.signal});

                const imageElement = ctx.root.querySelector(".dv-image");
                if (!(imageElement instanceof HTMLImageElement)) {
                    console.error("Image of class .dv-image does not exists");
                    return;
                }
                // console.log(imageElement);


                imageElement.addEventListener("click", () => ctx.root.focus(), {signal: ctx.ac.signal});


                const boundingBoxElement = ctx.root.querySelector(".dv-bounding-box");
                if (!(boundingBoxElement instanceof HTMLDivElement)) {
                    console.error("Div of class .dv-bounding-box does not exists.");
                    return;
                }
                // console.log(boundingBoxElement);

                const validationContainerElement = ctx.root.querySelector(".dv-detection-validation-container");
                if (!(validationContainerElement instanceof HTMLDivElement)) {
                    console.error("Div of class .dv-detection-validation-container does not exists.");
                    return;
                }
                // console.log(validationContainerElement);

                const inputElement = validationContainerElement.querySelector(".dv-roll-text-input");
                if (!(inputElement instanceof HTMLInputElement)) {
                    console.error("Input of class .dv-roll-text-input does not exists.");
                    return;
                }
                // console.log(inputElement);

                const acceptButton = validationContainerElement.querySelector(".dv-accept-button");
                if (!(acceptButton instanceof HTMLButtonElement)) {
                    console.error("Button of class .dv-accept-button does not exists.");
                    return;
                }
                // console.log(acceptButton);

                const rejectButton = validationContainerElement.querySelector(".dv-reject-button");
                if (!(rejectButton instanceof HTMLButtonElement)) {
                    console.error("Button of class .dv-reject-button does not exists.");
                    return;
                }
                // console.log(rejectButton);

                const navigationContainerElement = ctx.root.querySelector(".dv-index-navigation-container");
                if (!(navigationContainerElement instanceof HTMLDivElement)) {
                    console.error("Div of class .dv-index-navigation-container does not exists.");
                    return;
                }
                // console.log(navigationContainerElement);

                const prevButton = navigationContainerElement.querySelector(".dv-index-prev");
                if (!(prevButton instanceof HTMLButtonElement)) {
                    console.error("Button of class .dv-index-prev does not exists.");
                    return;
                }
                // console.log(prevButton)
            
                prevButton.addEventListener("click", () => ctx.args.setTriggerValue("index_step", -1), {signal: ctx.ac.signal});

                const nextButton = navigationContainerElement.querySelector(".dv-index-next");
                if (!(nextButton instanceof HTMLButtonElement)) {
                    console.error("Button of class .dv-index-next does not exists.");
                    return;
                }
                // console.log(nextButton);

                nextButton.addEventListener("click", () => ctx.args.setTriggerValue("index_step", 1), {signal: ctx.ac.signal});

                ctx.args = component;

                imageElement.src = `data:${data.image_mimetype};base64,${data.image_base64}`;

                const x1 = Math.floor(data.bounding_box[0] * imageElement.width / 1000);
                const y1 = Math.floor(data.bounding_box[1] * imageElement.height / 1000);
                const x2 = Math.floor(data.bounding_box[2] * imageElement.width / 1000);
                const y2 = Math.floor(data.bounding_box[3] * imageElement.height / 1000);
                // console.log(x1, y1, x2, y2);

                boundingBoxElement.style.left = `${x1}px`;
                boundingBoxElement.style.top = `${y1}px`;
                boundingBoxElement.style.width = `${x2 - x1}px`;
                boundingBoxElement.style.height = `${y2 - y1}px`;

                validationContainerElement.style.left = `${x1}px`;
                validationContainerElement.style.top = `${y2 + 8}px`;

                navigationContainerElement.style.left = `${x1 + 60}px`;
                navigationContainerElement.style.top = `${y2 + 58}px`;

                inputElement.value = data.rollno_text;
                // console.log(data.rollno_text);

                return () => ctx.ac?.abort();
            }
        """
    )

detection_visualizer = register_detection_visualizer()

class DetectionVisualizerData(TypedDict):
    """detection visualizer data typed dict"""
    index: int
    detections_count: int
    image_mimetype: str
    image_base64: str
    rollno_text: str
    bounding_box: list[int]

def create_detection_visualizer(
        data: DetectionVisualizerData,
        on_index_step_change: Callable[[], None]=lambda: None) -> None:
    """create a detection visualizer component"""
    detection_visualizer(
        key="detection_visualizer",
        data=data, on_index_step_change=on_index_step_change)

@streamlit.cache_resource
def register_counter():
    """register counter"""
    return streamlit.components.v2.component(
        "counter",
        html="""
            <div class="c-container">
                <button class="c-decr">decr</button>
                <span class="c-val"></span>
                <button class="c-incr">incr</button>
            </div>
        """,
        css="""
            .c-container {
                display: flex;
                flex-direction: row;
                gap: 4px;
                padding: 4px;
                border: 2px solid white;
            }
        """,
        js="""
            const MOD_ID = Math.random().toString(36).slice(2, 7);
            console.log("module loaded", MOD_ID);

            export default function(component) {
                const { parentElement, data } = component;

                let ctx = parentElement.__ctx;
                ctx?.ac?.abort();

                if (!ctx) {
                    const root = parentElement.querySelector(".c-container");
                    ctx = parentElement.__ctx = { root };
                }

                ctx.ac = new AbortController();

                const decrButton = ctx.root.querySelector(".c-decr");
                const incrButton = ctx.root.querySelector(".c-incr");

                decrButton.addEventListener(
                    "click", () => ctx.args.setTriggerValue("clicked", -1),
                    {signal: ctx.ac.signal});
                incrButton.addEventListener(
                    "click", () => ctx.args.setTriggerValue("clicked", 1),
                    {signal: ctx.ac.signal});

                ctx.root.addEventListener("keyup", (event) => {
                        console.log("module loaded", MOD_ID);
                        if (event.key === "ArrowLeft") {
                            console.log("ArrowLeft");
                            ctx.args.setTriggerValue("clicked", -1);
                        } else if (event.key === "ArrowRight") {
                            console.log("ArrowRight");
                            ctx.args.setTriggerValue("clicked", 1);
                        }
                }, {signal: ctx.ac.signal});

                ctx.args = component;
                ctx.root.querySelector(".c-val").textContent = data.count;

                return () => ctx.ac?.abort();
            }
        """
    )

counter = register_counter()

def create_counter(count: int, on_clicked_change: Callable[[], None]):
    """create counter"""
    counter(
        key="counter",
        data={"count": count},
        on_clicked_change=on_clicked_change)
