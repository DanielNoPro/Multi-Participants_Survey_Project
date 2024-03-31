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

    getSurveyStatistics(id, page, page_size) {
        return api.get(`api/v1/surveys/${id}/statistics/?page=${page}&page_size=${page_size}`)
    },

    getSurveyParticipants(id, page) {
        return api.get(`api/v1/surveys/${id}/participants/?page=${page}&page_size=10`)
    },

    activateSurvey(id){
        return api.patch(`api/v1/participants/${id}/activate/`)
    },

    deactivateSurvey(id){
        return api.patch(`api/v1/participants/${id}/deactivate/`)
    },

    createQuestionSet(survey_id, data){
        return api.post(`/api/v1/surveys/${survey_id}/sets/`, data)
    },

    getQuestionSets(survey_id, page, size){
        return api.get(`/api/v1/surveys/${survey_id}/sets/?page=${page}&page_size=${size}`)
    },

    deleteQuestionSet(survey_id, set_id){
        return api.delete(`/api/v1/surveys/${survey_id}/sets/${set_id}/`)
    },

    getSetPreConditions(survey_id, set_id){
        return api.get(`/api/v1/surveys/${survey_id}/sets/${set_id}/condition/?page=1&page_size=99`)
    },

    createSetPreConditions(survey_id, set_id, data){
        return api.post(`/api/v1/surveys/${survey_id}/sets/${set_id}/condition/`, data)
    },
    
    deleteSetPreCondition(survey_id, set_id, condition_id){
        return api.delete(`/api/v1/surveys/${survey_id}/sets/${set_id}/condition/${condition_id}`)
    },

    getNextSet(survey_id, set_id, data){
        return api.post(`/api/v1/surveys/${survey_id}/sets/${set_id}/surveys/next/`, data)
    }
}
