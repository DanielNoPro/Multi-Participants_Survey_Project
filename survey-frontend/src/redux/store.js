import { configureStore } from "@reduxjs/toolkit";
import surveyReducer from "./slices/surveySlice";
import questionReducer from "./slices/questionSlice";

export const store = configureStore({
    reducer: {
        survey: surveyReducer,
        question: questionReducer
    },
})