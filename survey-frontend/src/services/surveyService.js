import api from "@/constants/api"

export const surveyService = {
    getSurveys(page) {
        return api.get(`/api/v1/surveys/?page=${page}&page_size=10`)
    },

    getSurveyDetail(id) {
        return api.get(`/api/v1/surveys/${id}`)
    },

    createSurvey(data) {
        return api.post('/api/v1/surveys/', data)
    },

    deleteSurvey(id) {
        return api.delete(`/api/v1/surveys/${id}`)
    },

    updateSurvey(id, data) {
        return api.put(`/api/v1/surveys/${id}/`, data)
    },

    duplicateSurvey(id) {
        return api.post(`/api/v1/surveys/${id}/duplicate/`)
    },

    getSurveyQuestions(id, page) {
        return api.get(`api/v1/surveys/${id}/questions/?page=${page}&page_size=6`)
    },

    removeSurveyQuestion(survey_id, question_id) {
        return api.delete(`/api/v1/surveys/${survey_id}/questions/${question_id}/`)
    },

    addQuestionToSurvey(survey_id, data) {
        return api.post(`/api/v1/surveys/${survey_id}/questions/`, data)
    },

    sendSurvey(data) {
        return api.post(`/api/v1/survey/email`, data)
    },

    getSurveyStatistics(id){
        return api.get(`api/v1/surveys/${id}/statistics`)
    }

}
